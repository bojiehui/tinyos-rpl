/*
 * Copyright (c) 2008-2010 The Regents of the University  of California.
 * All rights reserved."
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * - Redistributions of source code must retain the above copyright
 *   notice, this list of conditions and the following disclaimer.
 * - Redistributions in binary form must reproduce the above copyright
 *   notice, this list of conditions and the following disclaimer in the
 *   documentation and/or other materials provided with the
 *   distribution.
 * - Neither the name of the copyright holders nor the names of
 *   its contributors may be used to endorse or promote products derived
 *   from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
 * THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

#include <IPDispatch.h>
#include <lib6lowpan/lib6lowpan.h>
#include <lib6lowpan/ip.h>
#include <lib6lowpan/ip.h>
#include "TestMessage.h"
#include "UDPReport.h"
#include "blip_printf.h"
#include <stdlib.h>
#define REPORT_PERIOD 10L

module UDPEchoP {
  uses {
    interface Boot;
    interface SplitControl as RadioControl;

#ifdef TOSSIM
#ifdef RPL_ROUTING
    interface RootControl;
#endif
#endif

    interface UDP as UDPSend;
    interface UDP as UDPReceive;

    interface Leds;

    interface Timer<TMilli> as StatusTimer;
    interface Timer<TMilli> as DelayTimer;	

    interface BlipStatistics<ip_statistics_t> as IPStats;
    interface BlipStatistics<udp_statistics_t> as UDPStats;

    interface Random;
  }

} implementation {
  bool timerStarted;
  nx_struct udp_report stats;
  struct sockaddr_in6 route_dest;
  radio_count_msg_t payload;
  struct sockaddr_in6 resp_dest;
  void *resp_data;
  uint16_t resp_len;
  uint16_t sequence_nr = 0;

  event void Boot.booted() {
    memclr((uint8_t *)&payload, sizeof(payload));
    dbg("Boot","Application Booted @ %s.\n",sim_time_string());
    call RadioControl.start();
    timerStarted = FALSE;
    call IPStats.clear();

#ifdef TOSSIM
#ifdef RPL_ROUTING
     if (TOS_NODE_ID == SOURCE_NODE_ID) {  
      if(TOS_NODE_ID == RPL_ROOT_ADDR){
        dbg ("UDPEchoP", "Root ID = %d.\n", TOS_NODE_ID);
        call RootControl.setRoot();
      }
 
      call UDPReceive.bind(SOURCE_NODE_PORT);
      call StatusTimer.startOneShot(1024*WAITTIME);
      route_dest.sin6_port = htons(DEST_NODE_PORT);
      inet_pton6(DEST_NODE_IP, &route_dest.sin6_addr); 
      dbg("UDPEchoP","Begin with Destination Node = %X:%X:%X on Port = %i   \n",ntohs(route_dest.sin6_addr.s6_addr16[0]), ntohs(route_dest.sin6_addr.s6_addr16[3]), ntohs(route_dest.sin6_addr.s6_addr16[7]), ntohs(route_dest.sin6_port));
    }
#endif
#endif

    if (TOS_NODE_ID != SOURCE_NODE_ID) {
      dbg ("UDPEchoP", "Node = %d.\n", TOS_NODE_ID);    
      call UDPReceive.bind(DEST_NODE_PORT);
    }
  }

  event void RadioControl.startDone(error_t e) {
  }

  event void RadioControl.stopDone(error_t e) {
  }

  event void StatusTimer.fired() {

    if (!timerStarted) {
      call StatusTimer.startPeriodic(PERIODIC_REQUEST);
      timerStarted = TRUE;
    }

  if (TOS_NODE_ID == SOURCE_NODE_ID) {
              
              if (ntohs(route_dest.sin6_addr.s6_addr16[7]) > NETWORK_SIZE){
                dbg("UDPEchoP","####################Finishing Ping################\n"); 
                call RadioControl.stop();
                exit(-1);
             }
          #ifdef PING_COUNT
          else if(stats.seqno == PING_COUNT){  
             route_dest.sin6_addr.s6_addr16[7] = htons((ntohs(route_dest.sin6_addr.s6_addr16[7]))+1); 
             dbg("UDPEchoP","Updated Dest Node ID = %i on Port = %i @ %s  \n",ntohs(route_dest.sin6_addr.s6_addr16[7]), ntohs(route_dest.sin6_port), sim_time_string()); 
      
            stats.seqno = 0;  
            sequence_nr = 0; 
         }
         #endif
        else { 
        stats.seqno++;  
        stats.sender = TOS_NODE_ID;
        payload.counter = sequence_nr++;
        payload.ist = WAITTIME;
        payload.senderID = SOURCE_NODE_ID;
        payload.receiverID = RPL_ROOT_ADDR;
        payload.data[0]= 0xFF;
        payload.data[DATA_SIZE-1]= 0xFF;

        call Leds.led1Toggle();
        dbg ("MsgExchange", "MsgExchange: Send: Node %i is sending UDP Message to Node = %X on Port = %i \n",TOS_NODE_ID, ntohs(route_dest.sin6_addr.s6_addr16[7]), ntohs(route_dest.sin6_port));
        dbg ("MsgExchange", "Send at %s SequenceNr: %i\n", sim_time_string(), payload.counter);
        dbg ("MsgRequests", "Request: Node: %i calls Node: %X SequenceNr: %i Time: %s \n",TOS_NODE_ID, ntohs(route_dest.sin6_addr.s6_addr16[7]), payload.counter, sim_time_string());

        call UDPSend.sendto(&route_dest, &payload, sizeof(payload));}
    }
   }

  event void UDPReceive.recvfrom(struct sockaddr_in6 *from, void *data,
                                 uint16_t len, struct ip6_metadata *meta) {
    //Binded to the listen port
    static char print_buf3[128];
    radio_count_msg_t * message_rec = (radio_count_msg_t *) data;
    memcpy(&resp_dest,from,sizeof(struct sockaddr_in6));

    resp_data = data;
    resp_len = len;

    inet_ntop6(&from->sin6_addr, print_buf3, 128);
    dbg ("MsgSuccessRecv", "Received Data from address = %s Port = %i SequenceNr: %i @ %s\n", print_buf3, ntohs(from->sin6_port), message_rec->counter, sim_time_string());
    dbg ("MsgExchange", "MsgExchange: Send: Sending response to address = %s Port = %i SequenceNr: %i @ %s\n", print_buf3, ntohs(from->sin6_port), message_rec->counter, sim_time_string());

    call DelayTimer.startOneShot(START_DELAY_TIMER);
    //call UDPReceive.sendto(&resp_dest, resp_data, resp_len);

  }

  event void UDPSend.recvfrom(struct sockaddr_in6 *from, void *data,
                              uint16_t len, struct ip6_metadata *meta) {
    radio_count_msg_t * message_rec = (radio_count_msg_t *) data;
    static char print_buf3[128];

    inet_ntop6(&from->sin6_addr, print_buf3, 128);
    dbg ("MsgExchange", "MsgExchange: Receive: Got response from address = %s Port = %i\n", print_buf3, ntohs(from->sin6_port));
    dbg ("MsgExchange", "Receive at %s SequenceNr: %i\n", sim_time_string(), payload.counter);
    dbg ("MsgRequests", "Response: Node: %s answered Node: %i SequenceNr: %i Time: %s\n",print_buf3, TOS_NODE_ID, message_rec->counter , sim_time_string());
}
  

 event void DelayTimer.fired() {
    
     dbg ("MsgExchange", "MsgExchange: Timer fired. Send to Node = %X:%X:%X on Port = %i   \n", ntohs(resp_dest.sin6_addr.s6_addr16[0]), ntohs(resp_dest.sin6_addr.s6_addr16[3]), ntohs(resp_dest.sin6_addr.s6_addr16[7]), ntohs(resp_dest.sin6_port) ); 

     call UDPReceive.sendto(&resp_dest, resp_data, resp_len); 
   } 
   } 
