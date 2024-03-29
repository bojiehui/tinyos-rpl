

#include "PrintfUART.h"
#include "bmp085.h"

module BMP085P{
  provides{
    interface Read<uint16_t> as Pressure;
    interface SplitControl as BMPSwitch;
  }
  uses {
   interface Resource;
   interface ResourceRequested;
   interface I2CPacket<TI2CBasicAddr> as I2CBasicAddr;     
   interface GeneralIO as Reset;
   interface Timer<TMilli> as TimeoutTimer;
  }
}

implementation{

  enum {
    S_STARTED,
    S_STOPPED,
    S_IDLE,
  };

  norace uint8_t state = S_IDLE;
  norace uint8_t bmp085cmd;
  norace uint8_t databuf[22];
  norace error_t error_return= FAIL;
  norace int32_t b5 = 0;
  norace int16_t temp;  // before to uint
  norace int32_t press = 0;
  norace int16_t pressure = 0;
  norace bool readPres = FALSE;
  norace bool readAlt = FALSE;

  // Calibration registers

  int16_t ac1 = 0;
  int16_t ac2 = 0;
  int16_t ac3 = 0;
  uint16_t ac4 = 0;
  uint16_t ac5 = 0;
  uint16_t ac6 = 0;
  int16_t b1 = 0;
  int16_t b2 = 0;
  int16_t mb = 0;
  int16_t mc = 0;
  int16_t md = 0;

  task void signalEvent(){
    if (error_return == SUCCESS){
      if (call TimeoutTimer.isRunning()) call TimeoutTimer.stop();
    }
    if (call Resource.isOwner()) call Resource.release();
    switch(bmp085cmd){
      case BMPCMD_READ_CALIB:
      case BMPCMD_START:
        if (error_return == SUCCESS) state = S_STARTED;
        signal BMPSwitch.startDone(error_return);
        break;

      case BMPCMD_READ_PRES:
        signal Pressure.readDone(error_return, pressure);
        break;
    }
  }

  task void clearBMP(){
    post signalEvent();
  }

  void calcTemp(uint32_t tmp){
    int32_t x1, x2 = 0;
    atomic{
      x1 = (((int32_t)tmp - (int32_t)ac6) * (int32_t)ac5) >> 15;
      x2 = ((int32_t)mc << 11) / (x1 + md);
      b5 = x1 + x2;
      // printfUART("B5 [%d]\n", b5);
      temp = (b5 + 8) >> 4;
    }
    // printfUART("Temp [%d.%d C]\n", temp/10, temp<<2);
  }

  void calcPres(int32_t tmp){
    uint32_t b4, b7 = 0;
    int32_t x1, x2, x3, b3, b6, p = 0;
    atomic{
      b6 = b5 - 4000; 
      x1 = (b2 * (b6 * b6 >> 12)) >> 11;
      x2 = ac2 * b6 >> 11;
      x3 = x1 + x2;
      b3 = ((((int32_t)ac1) * 4 + x3) + 2) >> 2;

      // printfUART("b6[%ld] x1[%ld] x2[%ld] x3[%ld] b3[%ld]\n", b6, x1, x2, x3, b3);

      x1 = (ac3 * b6) >> 13;
      x2 = (b1 * ((b6 * b6) >> 12)) >> 16;
      x3 = ((x1 + x2) + 2) >> 2;
      b4 = (ac4 * ((uint32_t)(x3 + 32768))) >> 15;
      b7 = ((uint32_t) tmp - b3) * 50000;

      // printfUART("b7[%lu] x1[%ld] x2[%ld] x3[%ld] b4[%lu]\n", b7, x1, x2, x3, b4);

      if (b7 < 0x80000000){
        p = (b7 << 1) / b4;
      } else {
        p = (b7 / b4) << 1;
      }

      x1 = (p >> 8) * (p >> 8);
      x1 = (x1 * 3038) >> 16;
      x2 = (-7357 * p) >> 16; 
      press = (p + ((x1 + x2 + 3791) >> 4));
      press /= 10;
      pressure = press;
    }
    // printfUART("Pressure [%u mbar]\n", pressure);
    readPres = FALSE;
    error_return = SUCCESS;
    post signalEvent();
  }

  command error_t BMPSwitch.start(){
    error_t e = FAIL;
    uint8_t i;
    error_return = FAIL;
    call TimeoutTimer.startOneShot(1024);
    if(state != S_STARTED){
      bmp085cmd = BMPCMD_START;
      for (i=0;i<22;i++) databuf[i] = 0;
      e = call Resource.request();
      if (e == SUCCESS) return SUCCESS;
    }
    return e;
  }

  command error_t BMPSwitch.stop(){
    error_t e = FAIL;
    if(state != S_STARTED){
      state = S_STOPPED;
      e = SUCCESS;  
    }
    signal BMPSwitch.stopDone(e);
    return e;
  }

  command error_t Pressure.read(){
    error_t e = FAIL;
    error_return = FAIL;
    call TimeoutTimer.startOneShot(1024);
    if (state == S_STARTED){
      bmp085cmd = BMPCMD_READ_UT;
      readPres = TRUE;
      e = call Resource.request();
      if (e == SUCCESS) return SUCCESS;
    }
    return e;
  }

  event void Resource.granted(){
    error_t e;
    switch(bmp085cmd){
      case BMPCMD_START:
        bmp085cmd = BMPCMD_READ_CALIB;
        databuf[0] = BMP085_AC1_MSB; // 0xAA	
        e = call I2CBasicAddr.write((I2C_START | I2C_STOP), BMP085_ADDR, 1, databuf);
        if (e != SUCCESS){
          printfUART("Retry\n");
         atomic P5OUT &= ~0x06;
         atomic P5REN &= ~0x06;
         post clearBMP();
        }
        break;

      case BMPCMD_READ_UT:
        databuf[0] = BMP085_CTLREG;   // 0xF4
        databuf[1] = BMP085_UT_NOSRX; // 0x2E	
        e = call I2CBasicAddr.write((I2C_START | I2C_STOP), BMP085_ADDR, 2, databuf);
        if (e != SUCCESS) printfUART("Error T:RG\n");
        break;

      case BMPCMD_READ_UP:
        databuf[0] = BMP085_CTLREG;   // 0xF4
        databuf[1] = BMP085_UP_OSRS0; // 0x34
        e = call I2CBasicAddr.write((I2C_START | I2C_STOP), BMP085_ADDR, 2, databuf);
        if (e != SUCCESS) printfUART("Error P:RG\n");
        break;
    }
  }

  async event void I2CBasicAddr.writeDone(error_t error, uint16_t addr, uint8_t length, uint8_t *data){
    error_t e;
    uint8_t i = 0;
    if(call Resource.isOwner()){
      switch(bmp085cmd){
        case BMPCMD_READ_UT:
        case BMPCMD_READ_UP:
            for (;i<0xFF;i++){} // delay
            if (bmp085cmd == BMPCMD_READ_UT){
              bmp085cmd = BMPCMD_READ_TEMP;
            } else {
              bmp085cmd = BMPCMD_READ_PRES;      
            }
            databuf[0] = BMP085_DATA_MSB;   // 0xF6
            e = call I2CBasicAddr.write((I2C_START | I2C_STOP), BMP085_ADDR, 1, databuf);
            if (e != SUCCESS) printfUART("Error WaitTimer [%d]\n", e);
          break;

        case BMPCMD_READ_CALIB:
          e = call I2CBasicAddr.read((I2C_START | I2C_STOP), BMP085_ADDR, 22, databuf);  
          break;

        case BMPCMD_READ_TEMP:
        case BMPCMD_READ_PRES:
          e = call I2CBasicAddr.read((I2C_START | I2C_STOP), BMP085_ADDR, 2, databuf);  
          break;
      }
    }
  }


  async event void I2CBasicAddr.readDone(error_t error, uint16_t addr, uint8_t length, uint8_t *data){
    int16_t utemp = 0;
    int32_t upres = 0;
    uint16_t i = 0;
    if (call Resource.isOwner()){
      switch(bmp085cmd){
        case BMPCMD_READ_CALIB:
          if (error == SUCCESS){
            atomic {
              ac1 = (data[0]<<8) + data[1];
              ac2 = (data[2]<<8) + data[3];
              ac3 = (data[4]<<8) + data[5];
              ac4 = (data[6]<<8) + data[7];
              ac5 = (data[8]<<8) + data[9];
              ac6 = (data[10]<<8) + data[11];
              b1 = (data[12]<<8) + data[13];
              b2 = (data[14]<<8) + data[15];
              mb = (data[16]<<8) + data[17];
              mc = (data[18]<<8) + data[19];
              md = (data[20]<<8) + data[21];
              // printCAL();
              error_return = SUCCESS;
              for (;i<0xFFFF;i++){}
              for (;i<0xFFFF;i++){}
            }
          }
          post signalEvent(); 
          break;

       case BMPCMD_READ_TEMP:
         utemp = (data[0]<<8) + data[1];
         calcTemp(utemp);
         break;

       case BMPCMD_READ_PRES:
         upres = ((int32_t)data[0] << 8) + (int32_t)data[1];
         calcPres(upres);
         break;
      }
      call Resource.release();
      if (readPres){
        bmp085cmd = BMPCMD_READ_UP;
        call Resource.request();
      }
    }
  }

  event void TimeoutTimer.fired(){
    post signalEvent();
  }
  
  async event void ResourceRequested.requested(){}  
  async event void ResourceRequested.immediateRequested(){}
  default event void Pressure.readDone(error_t error, uint16_t data){ return; }
}
