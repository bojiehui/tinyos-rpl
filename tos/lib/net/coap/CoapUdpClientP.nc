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

#include <net.h>
#include <tinyos_net.h>
#include <pdu.h>
#include <mem.h>

module CoapUdpClientP {
  provides interface CoAPClient;
  provides interface Init;
  uses interface Random;
  uses interface LibCoAP as LibCoapClient;
} implementation {
  coap_context_t *ctx_client;
  coap_queue_t *nextpdu;
  unsigned short tid;

  //generate random transaction id
  unsigned short get_tid(){
    if (!tid)
      tid = call Random.rand16();
    tid++;
    return ntohs(tid);
  }

  coap_pdu_t *
    coap_new_request( method_t m, coap_list_t *options, uint8_t *buf, uint8_t buflen ) {
    coap_pdu_t *pdu;
    coap_list_t *opt;

    if ( ! ( pdu = coap_new_pdu() ) )
      return NULL;

    pdu->hdr->type = COAP_MESSAGE_CON;
    pdu->hdr->id = get_tid();
    pdu->hdr->code = m;

    for (opt = options; opt; opt = opt->next) {
      coap_add_option( pdu, COAP_OPTION_KEY(*(coap_option *)opt->data),
		       COAP_OPTION_LENGTH(*(coap_option *)opt->data),
		       COAP_OPTION_DATA(*(coap_option *)opt->data) );
    }

    // Add buffer value to the PDU
    if (buflen) {
      if (!coap_add_data(pdu, buflen, buf))
	return NULL; //testing
    }

    return pdu;
  }

  coap_pdu_t *new_ack( coap_context_t  *ctx, coap_queue_t *node ) {
    coap_pdu_t *pdu;
    //printf("** coap: new_ack\n");
    GENERATE_PDU(pdu,COAP_MESSAGE_ACK,0,node->pdu->hdr->id);

    return pdu;
  }


  void message_handler(coap_context_t *ctx, coap_queue_t *node, void *data);

  command error_t Init.init() {

    ctx_client = (coap_context_t*)coap_malloc( sizeof( coap_context_t ) );
    if ( !ctx_client ) {
      return FAIL;
    }
    memset(ctx_client, 0, sizeof( coap_context_t ) );
    coap_register_message_handler( ctx_client, message_handler );
    return SUCCESS;
  }

  command error_t CoAPClient.request(struct sockaddr_in6 *dest,
				     method_t method,
				     coap_list_t *optlist,
				     uint8_t *buf,
				     uint8_t buflen) {
    coap_pdu_t *pdu;

    if (! (pdu = coap_new_request(method, optlist, buf, buflen)))
      return FALSE;

    dbg ("Coap", "CoAP: Send: Node %i is sending Message to Node = %X ... %X on Port = %i   \n",TOS_NODE_ID, ntohs(dest->sin6_addr.s6_addr16[0]), ntohs(dest->sin6_addr.s6_addr16[7]), ntohs(dest->sin6_port) );
    call LibCoapClient.send(ctx_client, dest, pdu, 1);
    return SUCCESS;
  };

  void message_handler(coap_context_t *ctx, coap_queue_t *node, void *data) {
    coap_pdu_t *pdu = NULL;


    if ( node->pdu->hdr->version != COAP_DEFAULT_VERSION ) {
      printf("dropped packet with unknown version %u\n", node->pdu->hdr->version);
      return;
    }

    //     if ( node->pdu->hdr->code < COAP_RESPONSE_100 && node->pdu->hdr->type == COAP_MESSAGE_CON ) {
    //       /* send 500 response */
    //       pdu = new_response( ctx, node, COAP_RESPONSE_500 );
    //       goto finish;
    //     }

    switch (node->pdu->hdr->code) {
    case COAP_RESPONSE_200:
      /* need to acknowledge if message was asyncronous */
      if ( node->pdu->hdr->type == COAP_MESSAGE_CON ) {
	pdu = new_ack( ctx, node );

	if ( pdu && (call LibCoapClient.send(ctx, &node->remote, pdu, 1) == COAP_INVALID_TID) ) {
	  printf("message_handler: error sending reponse");
	  coap_delete_pdu(pdu);
	  return;
	}
      }

    }
  }

  event void LibCoapClient.read(struct sockaddr_in6 *from, void *data,
				uint16_t len, struct ip6_metadata *meta) {
    coap_read(ctx_client, from, data, len, meta);
    coap_dispatch(ctx_client);
  }
  }
