/*
 * "Copyright (c) 2004-2005 The Regents of the University  of California.  
 * All rights reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its
 * documentation for any purpose, without fee, and without written agreement is
 * hereby granted, provided that the above copyright notice, the following
 * two paragraphs and the author appear in all copies of this software.
 * 
 * IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
 * DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT
 * OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY OF
 * CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 * THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS FOR A PARTICULAR PURPOSE.  THE SOFTWARE PROVIDED HEREUNDER IS
 * ON AN "AS IS" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATION TO
 * PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS."
 *
 * Copyright (c) 2002-2003 Intel Corporation
 * All rights reserved.
 *
 * This file is distributed under the terms in the attached INTEL-LICENSE     
 * file. If you do not find these files, copies can be found by writing to
 * Intel Research Berkeley, 2150 Shattuck Avenue, Suite 1300, Berkeley, CA, 
 * 94704.  Attention:  Intel License Inquiry.
 * @author Peter Trenkamp
 * @version $Revision: 1.0 $ $Date: 2011-05-02 17:00:59 $
 */

#ifndef RADIO_COUNT_TO_LEDS_H
#define RADIO_COUNT_TO_LEDS_H

enum {
  DATA_SIZE = 11,
  IST_SIZE = 24,
  AM_RADIO_COUNT_MSG = 10,
  AM_TEST_MSG = 10,
  NO_PACKET = 3000, //was 500 originally used by mote
  WAITTIME = 10000, //was 10000 originally used by mote
  PERIODIC_REQUEST = 1000, //was 10000 originally used by mote
  START_DELAY_TIMER = 10000, //to delay mote starting to send
  BUTTON_DELAY_TIMER = 5000,
};

uint16_t ist[IST_SIZE]= {128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128};

typedef nx_struct radio_count_msg {
  nx_uint16_t counter; //a[1]
  nx_uint16_t ist;//a[2]
  nx_uint8_t rssi;
  nx_uint8_t lqi;//a[4]
  nx_uint8_t power;
  nx_uint8_t distance;//a[6]
  nx_uint8_t senderID;
  nx_uint8_t receiverID;//a[8]
  nx_uint16_t voltage_sender;
  nx_uint16_t voltage_receiver;//a[10]
  nx_uint8_t crc_ok;
  nx_int8_t data[DATA_SIZE];
} radio_count_msg_t;

#endif
