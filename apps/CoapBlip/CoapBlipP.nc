/*
 * Copyright (c) 2011 University of Bremen, TZI
 * All rights reserved.
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
 */

#include <IPDispatch.h>
#include <lib6lowpan/lib6lowpan.h>
#include <lib6lowpan/ip.h>
#include "blip_printf.h"
#ifdef COAP_CLIENT_ENABLED
#include "tinyos_net.h"
#endif

module CoapBlipP {
  uses {
    interface Boot;
    interface SplitControl as RadioControl;
#ifdef COAP_SERVER_ENABLED
    interface CoAPServer;
#ifdef COAP_RESOURCE_KEY
    interface Mount;
#endif
#endif
#ifdef COAP_CLIENT_ENABLED
    interface CoAPClient;
#ifdef COAP_CLIENT_SEND_RI
    interface Timer<TMilli> as Timer;
    interface ReadResource[uint8_t uri];
#endif
#endif
    interface Leds;
  }
  provides interface Init;
} implementation {
#ifdef COAP_CLIENT_ENABLED
  struct sockaddr_in6 sa6;
  uint8_t node_integrate_done = FALSE;
  coap_list_t *optlist = NULL;

#endif

  command error_t Init.init() {
    return SUCCESS;
  }

  event void Boot.booted() {
#ifdef COAP_SERVER_ENABLED
    uint8_t i;
#endif
    call RadioControl.start();
    printf("booted %i start\n", TOS_NODE_ID);
#ifdef COAP_SERVER_ENABLED
#ifdef COAP_RESOURCE_KEY
    if (call Mount.mount() == SUCCESS) {
      printf("CoapBlipP.Mount successful\n");
    }
#endif
    // needs to be before registerResource to setup context:
    call CoAPServer.bind(COAP_SERVER_PORT);

    for (i=0; i < NUM_URIS; i++) {
      call CoAPServer.registerResource(uri_key_map[i].uri,
				       uri_key_map[i].urilen - 1,
				       uri_key_map[i].mediatype,
				       uri_key_map[i].writable,
				       uri_key_map[i].splitphase,
				       uri_key_map[i].immediately);
    }
#endif

  }

#if defined (COAP_SERVER_ENABLED) && defined (COAP_RESOURCE_KEY)
  event void Mount.mountDone(error_t error) {
  }
#endif

  event void RadioControl.startDone(error_t e) {
    printf("radio startDone: %i\n", TOS_NODE_ID);
  }

  event void RadioControl.stopDone(error_t e) {
  }

#ifdef COAP_CLIENT_ENABLED
  event void ForwardingTableEvents.defaultRouteAdded() {
#ifdef COAP_CLIENT_ENABLED
    inet_pton6(COAP_CLIENT_DEST, &sa6.sin6_addr);
    sa6.sin6_port = htons(COAP_CLIENT_PORT);
#ifdef COAP_CLIENT_SEND_NI
    if (node_integrate_done == FALSE) {
      node_integrate_done = TRUE;
      coap_insert( &optlist, new_option_node(COAP_OPTION_URI_PATH, sizeof("ni") - 1, "ni"), order_opts);

      call CoAPClient.request(&sa6, COAP_REQUEST_PUT, optlist, NULL, 0);
    }
#endif
#ifdef COAP_CLIENT_SEND_RI
    optlist = NULL;
    coap_insert( &optlist, new_option_node(COAP_OPTION_URI_PATH, sizeof("ri") - 1, "ri"), order_opts);
    call Timer.startOneShot(1024);
#endif
#endif
    call Leds.led2On();
  }

#if defined (COAP_CLIENT_ENABLED) && defined (COAP_CLIENT_SEND_RI)
  event void Timer.fired() {
    call ReadResource.get[KEY_ROUTE_CLIENT](0);
  }
#endif

  event void ForwardingTableEvents.defaultRouteRemoved() {
  }


#ifdef COAP_CLIENT_ENABLED
  event void CoAPClient.request_done() {
    //TODO: handle the request_done
  };
#ifdef  COAP_CLIENT_SEND_RI
  event void ReadResource.getDone[uint8_t uri_key](error_t result,
						   coap_tid_t id,
						   uint8_t asyn_message,
						   uint8_t* val_buf,
						   uint8_t buflen) {

    if (result == SUCCESS) {
      call Leds.led0Toggle();
      call CoAPClient.request(&sa6, COAP_REQUEST_PUT, optlist, val_buf, buflen);
    }

    call Timer.startPeriodic(1024 * COAP_CLIENT_SEND_RI_INTERVAL);
  }

 default command error_t ReadResource.get[uint8_t uri_key](coap_tid_t id) {
   //printf("** coap: default (get not available for this resource)....... %i\n", uri_key);
   call Leds.led2Toggle();
   return FAIL;
 }
 event void ReadResource.getDoneDeferred[uint8_t uri_key](coap_tid_t id) {
 }
#endif
#endif

  }
