/*
 * Copyright (c) 2010 Johns Hopkins University. All rights reserved.
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
 * - Neither the name of the copyright holder nor the names of
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
 * OF THE POSSIBILITY OF SUCH DAMAGE. */

/**
 * RPLRankP.nc
 * @ author JeongGil Ko (John) <jgko@cs.jhu.edu>
 */

/*
 * Copyright (c) 2010 Stanford University. All rights reserved.
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
 * - Neither the name of the copyright holder nor the names of
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

/**
 * @ author Yiwei Yao <yaoyiwei@stanford.edu>
 */

#include <RPL.h>
#include <lib6lowpan/ip.h>
#include <lib6lowpan/iovec.h>
#include <lib6lowpan/ip_malloc.h>

#include "blip_printf.h"
#include "IPDispatch.h"

module RPLRankP{
  provides{
    interface RPLRank as RPLRankInfo;
    interface StdControl;
    interface IP as IP_DIO_Filter;
    interface RPLParentTable;
  }
  uses {
    interface IP as IP_DIO;
    interface IPPacket;
    interface RPLRoutingEngine as RouteInfo;
    interface Leds;
    interface IPAddress;
    interface ForwardingTable;
    interface ForwardingEvents;
    interface RPLOF;
  }
}

implementation {

  uint16_t nodeRank = INFINITE_RANK; // 0 is the initialization state
  uint16_t minRank = INFINITE_RANK;
  bool leafState = FALSE;
  /* SDH : this is essentially the Default Route List */
  struct in6_addr prevParent;
  uint32_t parentChanges = 0;
  uint8_t parentNum = 0;
  uint16_t VERSION = 0;
  uint16_t nodeEtx = divideRank;
  uint16_t MAX_RANK_INCREASE = 1;
  //uint16_t MIN_HOP_RANK_INCREASE = 1;
  
  uint8_t etxConstraint;
  uint32_t latencyConstraint;
  bool hasConstraint[2] = {FALSE,FALSE}; //hasConstraint[0] represents ETX, hasConstraint[1] represent Latency
  
  struct in6_addr DODAGID;
  struct in6_addr DODAG_MAX;
  uint8_t METRICID; //which metric
  uint16_t OCP;
  uint32_t myQDelay = 1.0;
  bool hasOF = FALSE;
  uint8_t Prf = 0xFF;
  uint8_t alpha; //configuration parameter
  uint8_t beta;
  bool ignore = FALSE;
  bool ROOT = FALSE;
  bool m_running = FALSE;
  //uint8_t divideRank = 128;
  parent_t parentSet[MAX_PARENT];
 
  void resetValid();
  void getNewRank();

// #define printf(X, fmt ...) ;
// #define printf_in6addr(X) ;

#define RPL_GLOBALADDR

  bool compare_ipv6(struct in6_addr* node1, struct in6_addr* node2){
    return !memcmp((node1), (node2), sizeof(struct in6_addr));
  }

  void memcpy_rpl(uint8_t* a, uint8_t* b, uint8_t len){
    //memcpy(a, b, len);
    uint8_t i;
    for (i = 0 ; i < len ; i++)
      a[i] = b[i];

  }

#define RPL_GLOBALADDR

  command error_t StdControl.start() { //initialization
    uint8_t indexset;

    DODAG_MAX.s6_addr16[7] = htons(0);

    memcpy_rpl((uint8_t*)&DODAGID, (uint8_t*)&DODAG_MAX, sizeof(struct in6_addr));

    for (indexset = 0; indexset < MAX_PARENT; indexset++) {
      parentSet[indexset].valid = FALSE;
    }

    m_running = TRUE;
    return SUCCESS;
  }

  command error_t StdControl.stop() { 
    m_running = FALSE;
    return SUCCESS;
  }

  command parent_t* RPLParentTable.get(uint8_t i){
    return &parentSet[i];
  }

  // declare the I am the root
  command void RPLRankInfo.declareRoot(){ //done
    ROOT = TRUE;
    // minMetric = divideRank;
    nodeRank = ROOT_RANK;
  }

  command bool RPLRankInfo.validInstance(uint8_t instanceID){ //done
    return TRUE;
  }

  // I am no longer a root
  command void RPLRankInfo.cancelRoot(){ //done
  }

  uint8_t getParent(struct in6_addr *node);
  
  // return the rank of the specified IP addr
  command uint16_t RPLRankInfo.getRank(struct in6_addr *node){ //done
    uint8_t indexset;
    struct in6_addr my_addr;
    //   dbg("RPLRank","RPLRank: my_addr = ");
    // printf_in6addr_dbg(&my_addr);
#ifdef RPL_GLOBALADDR
    call IPAddress.getGlobalAddr(&my_addr);
#else
    call IPAddress.getLLAddr(&my_addr);
#endif
    
    if(compare_ipv6(&my_addr, node)){

      if(ROOT){
	nodeRank = ROOT_RANK;
      }
      return nodeRank;
    }

    indexset = getParent(node);

    if (indexset != MAX_PARENT){
      dbg("RPLRank","RPLRank: parentSet[%u] = %u\n",indexset, parentSet[indexset].rank);
      return parentSet[indexset].rank;
    }

    return 0x1234;
  }

  command error_t RPLRankInfo.getDefaultRoute(struct in6_addr *next) {
    //printf_in6addr(&parentSet[desiredParent].parentIP);
    //printf("\n");
    if (parentNum) {
      memcpy_rpl((uint8_t*)next, (uint8_t*)call RPLOF.getParent(), sizeof(struct in6_addr));
      return SUCCESS;
    }
    return FAIL;
  }

  bool exceedThreshold(uint8_t indexset, uint8_t ID) { //done
    dbg("RPLRank","RPLRank: exceedThreshold %u %u\n",
        parentSet[indexset].etx_hop, ETX_THRESHOLD);
    return parentSet[indexset].etx_hop > ETX_THRESHOLD;
  }

  command bool RPLRankInfo.compareAddr(struct in6_addr *node1, struct in6_addr *node2){ //done
    return compare_ipv6(node1, node2);
  }

  //return the index of parent
  uint8_t getParent(struct in6_addr *node) { //done
    uint8_t indexset;
    if (parentNum == 0) {
      return MAX_PARENT;
    }
    for (indexset = 0; indexset < MAX_PARENT; indexset++) {

      if (compare_ipv6(&(parentSet[indexset].parentIP),node) && 
          parentSet[indexset].valid) {
	return indexset;
      }
    }
    return MAX_PARENT;
  }

  // return if IP is in parent set
  command bool RPLRankInfo.isParent(struct in6_addr *node) { //done
    return (getParent(node) != MAX_PARENT);
  }

  /*
  // new iteration has begun, all need to be cleared
  command void RPLRankInfo.notifyNewIteration(){ //done
    parentNum = 0;
    resetValid();
  }
  */

  void resetValid(){    //done
    uint8_t indexset;
    dbg("RPLRank","RPLRank: resetValid()\n");
    for (indexset = 0; indexset < MAX_PARENT; indexset++) {
      parentSet[indexset].valid = FALSE;
    }
  }

  // inconsistency is seen for the link with IP
  // record this as part of entry in table as well
  // Other layers will report this information
  command void RPLRankInfo.inconsistencyDetected(){ //done
    parentNum = 0;
    call RPLOF.resetRank();
    dbg("RPLRank","RPLRank: inconsistencyDetected,nodeRank = Infinite, resetValid()\n");
    nodeRank = INFINITE_RANK;
    resetValid();
    //memcpy(&DODAGID, 0, 16);
    //call RouteInfo.inconsistency();
  }

  // ping rank component if there are parents
  command uint8_t RPLRankInfo.hasParent(){ //done
    return parentNum;
  }

  command bool RPLRankInfo.isLeaf(){ //done
    //return TRUE;
    return leafState;
  }

  uint8_t getPreExistingParent(struct in6_addr *node) {
    // just find if there are any pre existing information on this node...
    uint8_t indexset;
    if (parentNum == 0) {
      dbg("RPLRank","RPLRank: parentNum = 0\n");
      return MAX_PARENT;
    }

    for (indexset = 0; indexset < MAX_PARENT; indexset++) {
      if (compare_ipv6(&(parentSet[indexset].parentIP),node)) {
        dbg("RPLRank","RPLRank: pre-existingParent index = %u\n", indexset);
	return indexset;
      }
    }
    return MAX_PARENT;
  }

  command uint16_t RPLRankInfo.getEtx(){ //done
    return call RPLOF.getObjectValue();
  }

  void insertParent(parent_t parent) {
    uint8_t indexset;
    uint16_t tempEtx_hop;

    dbg("RPLRank","RPLRank: insert parent.parentIP = %u\n", (uint8_t)htons(&parent.parentIP.s6_addr16[7]));
    indexset = getPreExistingParent(&parent.parentIP);

    //printf("Insert Node: %d \n", indexset);

    if(indexset != MAX_PARENT) // we have previous information
      {
        dbg("RPLRank","RPLRank: i have previous information\n");
	tempEtx_hop = parentSet[indexset].etx_hop;
	parentSet[indexset] = parent;

	if(tempEtx_hop > INIT_ETX && tempEtx_hop < BLIP_L2_RETRIES){
	  tempEtx_hop = tempEtx_hop-INIT_ETX;
	  if(tempEtx_hop < divideRank)
	    tempEtx_hop = INIT_ETX;
	}else{
	  tempEtx_hop = INIT_ETX;
	}

        dbg("RPLRank","RPLRank: before ParentSet[%i].etx_hop = %u\n",indexset, parentSet[indexset].etx_hop); 
	parentSet[indexset].etx_hop = tempEtx_hop;
        dbg("RPLRank","RPLRank: ParentSet[%i].etx_hop = %u\n",indexset, parentSet[indexset].etx_hop); 
	parentNum++;
	dbg("RPLRank","RPLRank: Parent Added, total # of parents = %d \n",parentNum);
	return;
      }
    else {
      dbg("RPLRank","RPLRank: i don't have previous information. \n");
    }

    for (indexset = 0; indexset < MAX_PARENT; indexset++) {
      dbg("RPLRank","RPLRank: indexset %u, Max_parent = %u\n",indexset, MAX_PARENT);
      // check the first empty entry in parentSet
      if (!parentSet[indexset].valid) {
        dbg("RPLRank","RPLRank: # %u in parentSet is not valid, asigin this entry with parent %u\n",indexset,(uint8_t)htons(parent.parentIP.s6_addr16[7]));
	parentSet[indexset] = parent;
	parentNum++;
	break;
      }
    }
    //printf("Parent Added 2 %d \n",parentNum);
  }

  void evictParent(uint8_t indexset) {//done
    dbg("RPLRank","RPLRank: evictParent %u\n", indexset);

    parentSet[indexset].valid = FALSE;
    parentNum--;
    printf("Evict parent indexset = %u \n", indexset);
    if (parentNum == 0) {
      //should do something
      dbg("RPLRank","RPLRank: paren Number = 0\n");
      call RouteInfo.resetTrickle();
    }
  }

  task void newParentSearch(){
    // only called when evictAll just cleared out my current desired parent
    dbg("RPLRank","evictAll: recomputeRoutes 0\n");   
    call RPLOF.recomputeRoutes();
    getNewRank();
  }

  /* check and remove parents on rank change */
  void evictAll() {//done
    uint8_t indexset, myParent;
    dbg("RPLRank","RPLRank: evitAll()\n");
    myParent = getParent(call RPLOF.getParent());
    dbg("RPLRank","RPLRank: myParent index = %u\n",myParent);

    for (indexset = 0; indexset < MAX_PARENT; indexset++) {
      if (parentSet[indexset].valid && parentSet[indexset].rank >= nodeRank) {
        dbg("RPLRank","RPLRank: evict parentSet[%u]: parent node: %u\n",
            indexset, (uint8_t)htons(parentSet[indexset].parentIP.s6_addr[17]));
	parentSet[indexset].valid = FALSE;
	parentNum--;
        printf("Evict all: parentNum: %d\n", parentNum);
	if(indexset == myParent){
	  // i just cleared out my own parent...
	  post newParentSearch();
	  return;
	}
      }
    }
  }

  command void RPLRankInfo.setQueuingDelay(uint32_t delay){    
    myQDelay = delay;
  }

#if 0
  event error_t ForwardingEvents.deleteHeader(struct ip6_hdr *iph, void* payload){
    uint16_t len;
    /* Reconfigure length */
    len = ntohs(iph->ip6_plen);
    //printf("delete header %d \n",len);
    len = len - sizeof(rpl_data_hdr_t);;
    iph->ip6_plen = htons(len);

    /* Move data back up */
    memcpy_rpl((uint8_t*)payload, (uint8_t*)payload + sizeof(rpl_data_hdr_t), len);

    /* configure length*/
    //&length -= sizeof(sizeof(rpl_data_hdr_t));

    return SUCCESS;
  }
#endif


  event bool ForwardingEvents.initiate(struct ip6_packet *pkt,
                                       struct in6_addr *next_hop) {
    uint16_t len; 
    static struct ip_iovec v;
    static rpl_data_hdr_t data_hdr;
   printf_dbg("RankP forwarding initiate 1 \n");
#ifndef RPL_OF_MRHOF
    return TRUE;
#endif
    printf_dbg("RankP forwarding initiate \n");
    if(pkt->ip6_hdr.ip6_nxt == IANA_ICMP)
      return TRUE;

    data_hdr.ip6_ext_outer.ip6e_nxt = pkt->ip6_hdr.ip6_nxt;
    data_hdr.ip6_ext_outer.ip6e_len = 0; 

    data_hdr.ip6_ext_inner.ip6e_nxt = RPL_HBH_RANK_TYPE; /* well, this is actually the type */
    data_hdr.ip6_ext_inner.ip6e_len = sizeof(rpl_data_hdr_t) - 
      offsetof(rpl_data_hdr_t, bitflag);
    data_hdr.bitflag = 0;
    data_hdr.bitflag = 0 << RPL_DATA_O_BIT_SHIFT;
    data_hdr.bitflag |= 0 << RPL_DATA_R_BIT_SHIFT;
    data_hdr.bitflag |= 0 << RPL_DATA_F_BIT_SHIFT;
    //data_hdr.o_bit = 0;
    //data_hdr.r_bit = 0;
    //data_hdr.f_bit = 0;
    //data_hdr.reserved = 0;
    data_hdr.instance_id = call RouteInfo.getInstanceID();
    data_hdr.senderRank = nodeRank;
    pkt->ip6_hdr.ip6_nxt = IPV6_HOP;

    len = ntohs(pkt->ip6_hdr.ip6_plen);

    /* add the header */
    v.iov_base = (uint8_t*) &data_hdr;
    v.iov_len = sizeof(rpl_data_hdr_t);
    v.iov_next = pkt->ip6_data; // original upper layer goes here!
    
    /* increase length in ipv6 header and relocate beginning*/
    pkt->ip6_data = &v;
    len = len + v.iov_len;
    pkt->ip6_hdr.ip6_plen = htons(len);

    // iov_print(&v); printfflush();
    
    return TRUE;

  }

  /**
   * Signaled by the forwarding engine for each packet being forwarded.
   *
   * If we return FALSE, the stack will drop the packet instead of
   * doing whatever was in the routing table.
   *
   */
  event bool ForwardingEvents.approve(struct ip6_packet *pkt, 
                                      struct in6_addr *next_hop) {

    rpl_data_hdr_t data_hdr;
    bool inconsistent = FALSE;
    uint8_t o_bit;
    uint8_t nxt_hdr = IPV6_HOP;
    int off;
printf_dbg("RankP forwarding approve 1 \n");
#ifndef RPL_OF_MRHOF
    return TRUE;
#endif
 printf_dbg("RankP forwarding approve \n");
    /* is there a HBH header? */
    off = call IPPacket.findHeader(pkt->ip6_data, pkt->ip6_hdr.ip6_nxt, &nxt_hdr); 
    if (off < 0) return TRUE;
    /* if there is, is there a RPL TLV option in there? */
    off = call IPPacket.findTLV(pkt->ip6_data, off, RPL_HBH_RANK_TYPE);
    if (off < 0) return TRUE;
    /* read out the rpl option */
    if (iov_read(pkt->ip6_data, 
                 off + sizeof(struct tlv_hdr), 
                 sizeof(rpl_data_hdr_t) - offsetof(rpl_data_hdr_t, bitflag), 
                 (void *)&data_hdr.bitflag) != 
        sizeof(rpl_data_hdr_t) - offsetof(rpl_data_hdr_t, bitflag))
      return TRUE;
    o_bit = (data_hdr.bitflag & RPL_DATA_O_BIT_MASK) >> RPL_DATA_O_BIT_SHIFT ;
    //printf("approve test: %d %d %d %d %d \n", data_hdr.senderRank, data_hdr.instance_id, nodeRank, o_bit, call RPLRankInfo.getRank(next_hop));

    /* SDH : we'd want to dispatch on the instance id if there are
       multiple dags */

    if (data_hdr.senderRank == ROOT_RANK){
      o_bit = 1;
      goto approve;
    }

    if (o_bit && data_hdr.senderRank > nodeRank) {
      /* loop */
      inconsistent = TRUE;
    } else if (!o_bit && data_hdr.senderRank < nodeRank) {
      inconsistent = TRUE;
    }

    if (call RPLRankInfo.getRank(next_hop) >= nodeRank){
      /* Packet is heading down if the next_hop rank is not smaller than the current one (not in the parent set) */
      /* By the time I am here, it means that there is a next hop but if this is not in my parent set, then it should be downward */
      data_hdr.bitflag |= 1 << RPL_DATA_O_BIT_SHIFT;
      //data_hdr.o_bit = 1;
    }

    if (inconsistent) {
      if ((data_hdr.bitflag & RPL_DATA_R_BIT_MASK) >> RPL_DATA_R_BIT_SHIFT) {
        /*  this is not the first time  */
        /*  ditch this packet! */
	call RouteInfo.inconsistency();
	//printf("NOT Approving: %d %d %d\n", data_hdr.senderRank, data_hdr.instance_id, inconsistent);
        return FALSE;
      } else {
        /* just mark it */
	data_hdr.bitflag |= 1 << RPL_DATA_R_BIT_SHIFT;
        //data_hdr.r_bit = 1;
	//chooseDesired();
	//call RPLOF.recomputeRoutes();
	//recaRank();
	//getNewRank();
	//call RouteInfo.inconsistency();
	goto approve;
      }
    }

  approve:
    //printf("Approving: %d %d %d\n", data_hdr.senderRank, data_hdr.instance_id, inconsistent);
    data_hdr.senderRank = nodeRank;
    // write back the modified data header
    iov_update(pkt->ip6_data, 
               off + sizeof(struct tlv_hdr), 
               sizeof(rpl_data_hdr_t) - offsetof(rpl_data_hdr_t, bitflag), 
               (void *)&data_hdr.bitflag);
    return TRUE;
  }

  /*  Compute ETX! */
  event void ForwardingEvents.linkResult(struct in6_addr *node, struct send_info *info) {
    uint8_t indexset, myParent;
    uint16_t etx_now = info->link_transmissions;

    //printf("linkResult: ");
    //dbg("RPLRank","RPLRank:linkResult: ");
    printf_in6addr_dbg(node);
    dbg("RPLRank","RPLRank: linkResult %d [%i] %d \n", TOS_NODE_ID, info->link_transmissions, nodeRank);

    myParent = getParent(call RPLOF.getParent());

    if(nodeRank == ROOT_RANK) { //root
      return;
    }

    for (indexset = 0; indexset < MAX_PARENT; indexset++) {
      if (parentSet[indexset].valid && 
          compare_ipv6(&(parentSet[indexset].parentIP), node)){
        dbg("RPLRank","RPLRank: first valid parent index = %u\n",indexset);
	break;
      }
    }

    if (indexset != MAX_PARENT) { // not empty...,
      dbg("RPLRank","RPLRank: calculate etx_hop: [parentSet[%i].etx_hop(%u)*6 + etx_now(%u)*divideRank(%i)*4]/10\n", indexset, parentSet[indexset].etx_hop, etx_now, divideRank);
      parentSet[indexset].etx_hop = (parentSet[indexset].etx_hop * 6 + (etx_now * divideRank) * 4) / 10; // 60% old, 40% new
      dbg("RPLRank","RPLRank: parentSet[%i]= %u\n", indexset, (uint8_t)htons(parentSet[indexset].parentIP.s6_addr16[7]));
      dbg("RPLRank","RPLRank: new parent etx_hop = %u\n", parentSet[indexset].etx_hop);
      dbg("RPLRank","RPLRank: exceedThreshold? %i, etx_now = %u\n",exceedThreshold(indexset, METRICID),etx_now);
      dbg("RPLRank","RPLRank: BLIP_L2_RETRIES= %u\n",BLIP_L2_RETRIES);

      if (exceedThreshold(indexset, METRICID) || etx_now == BLIP_L2_RETRIES) {
	evictParent(indexset);
	if(indexset == myParent && parentNum > 0){
          dbg("RPLRank","RPLRank: RecomputeRoutes1\n");
	  call RPLOF.recomputeRoutes();}
      }

      /*
      else if(etx_now > 1 && parentNum > 1){ // if a packet is not transmitted on its first try... see if there is something better...
	call RPLOF.recomputeRoutes();
      }
      */
      dbg("RPLRank","RPLRank: getNewRank 1\n");
      getNewRank();

      //printf(">> P_ETX UPDATE %d %d %d %d %d %d\n", indexset, parentSet[indexset].etx_hop, etx_now, ntohs(parentSet[indexset].parentIP.s6_addr16[7]), nodeRank, parentNum);

      return;
    }
    // not contained in either parent set, do nothing
  }

  /* old <= new, return true;  */
  bool compareParent(parent_t oldP, parent_t newP) { 
    return (oldP.etx_hop + oldP.etx) <= (newP.etx_hop + newP.etx);
  }

  void getNewRank(){
    uint16_t prevRank = nodeRank;//, myParent;
    bool newParent = FALSE;
    //    struct in6_addr ADDR_MY_IP;
    printf("getNewRank: 1 prev node rank: %u  \n",prevRank);
    // call IPAddress.getGlobalAddr(&ADDR_MY_IP);
    //  printf("getNewRank: 1 new rank: %i  \n",call RPLRankInfo.getRank(&ADDR_MY_IP));
    newParent = call RPLOF.recalcualateRank();//hier gehts dahin
    printf("getNewRank: 2 new Parent?: %i  \n",newParent);
    // printf("getNewRank: 2 new rank: %i  \n",call RPLRankInfo.getRank(&ADDR_MY_IP));
    nodeRank = call RPLOF.getRank();
    printf("getNewRank: 3 new node rank: %u  \n",nodeRank);
    //printf("getNewRank: 3 new rank: %i  \n",call RPLRankInfo.getRank(&ADDR_MY_IP));

    if(newParent){
      dbg("RPLRank","RPLRank: newParent\n");
      minRank = nodeRank;
      return;
    }

    if(nodeRank <= minRank){
      dbg("RPLRank","RPLRank: nodeRank <= minRank\n");
      minRank = nodeRank;
      return;
    }

    // did the node rank get worse than the limit?
    dbg("RPLRank","RPLRank: nodeRank = %d, prevRank = %d\n",nodeRank,prevRank);
    dbg("RPLRank","RPLRank: minRank = %d, MAX_RANK_INCREASE = %d\n",minRank,MAX_RANK_INCREASE);
    if (nodeRank > prevRank && 
        nodeRank - minRank > MAX_RANK_INCREASE &&
        MAX_RANK_INCREASE != 0) {
      // this is inconsistency!
      //call RPLOF.recomputeRoutes();
      printf("Inconsistent %d, nodeRank = infinite\n", TOS_NODE_ID);
      nodeRank = INFINITE_RANK;
      minRank = INFINITE_RANK;
      call RouteInfo.inconsistency();
      return;
    }
    
    evictAll();
  }

  void parseDIO(struct ip6_hdr *iph, struct dio_base_t *dio) { 
    uint16_t pParentRank;
    struct in6_addr rDODAGID;
    uint16_t etx = 0xFFFF;
    parent_t tempParent;
    uint8_t parentIndex, myParent;
    uint16_t preRank;
    uint8_t tempPrf;
    bool newDodag = FALSE;

    struct dio_body_t* dio_body;
    struct dio_metric_header_t* dio_metric_header;
    struct dio_etx_t* dio_etx;
    struct dio_dodag_config_t* dio_dodag_config;
    struct dio_prefix_t* dio_prefix;
    uint8_t* newPoint;
    uint16_t trackLength = ntohs(iph->ip6_plen);
    struct in6_addr ADDR_MY_IP;
    call IPAddress.getGlobalAddr(&ADDR_MY_IP);
    printf("parseDIO is called!!! node rank = %u\n",nodeRank);
    /* I am root */
    if (nodeRank == ROOT_RANK){
      printf("NodeRank = Root_Rank \n");
      return;
    } 

    /* new iteration */
    if (dio->version != VERSION && compare_ipv6(&dio->dodagID, &DODAGID)) {
      // printf("new iteration!\n");
      parentNum = 0;
      VERSION = dio->version;
      dbg("RPLRank","RPLRank: new iteration, call resetRank, resetValid\n");
      call RPLOF.resetRank();
      //printf("Status Rank: %i nach Reset noderank =infinite\n",call RPLRankInfo.getRank(&ADDR_MY_IP));
      nodeRank = INFINITE_RANK;
      minRank = INFINITE_RANK;
      resetValid();
    }
/* printf_dbg("Wo isser denn 2 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
    //if (dio->dagRank >= nodeRank && nodeRank != INFINITE_RANK) return;

    printf("source node %d, DIO in Rank:%u, nodeRank:%u parentNum:%d\n", ntohs(iph->ip6_src.s6_addr16[7]), dio->dagRank, nodeRank, parentNum);
    //printf_in6addr(&iph->ip6_src);
    //printf("\n");
    
    pParentRank = dio->dagRank;
    // DODAG ID in this DIO packet (received DODAGID)

    memcpy_rpl((uint8_t*)&rDODAGID, (uint8_t*)&dio->dodagID, sizeof(struct in6_addr));
    tempPrf = dio->flags.flags_chunk & DIO_PREF_MASK;
/* printf_dbg("Wo isser denn 3 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
    if (!compare_ipv6(&DODAGID, &DODAG_MAX) && 
        !compare_ipv6(&DODAGID, &rDODAGID)) { 
/* printf_dbg("Wo isser denn 4 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
      // I have a DODAG but this packet is from a new DODAG
      if (Prf < tempPrf) { //ignore
	//printf("LESS PREFERENCE IGNORE \n");
	ignore = TRUE;
	return;
      } else if (Prf > tempPrf) { //move
        //printf("MOVE TO NEW DODAG \n");
        dbg("MRHOF","NEW DODAG\n");
	Prf = tempPrf;
	memcpy_rpl((uint8_t*)&DODAGID, (uint8_t*)&rDODAGID, sizeof(struct in6_addr));
	parentNum = 0;
/* printf_dbg("Wo isser denn 5 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
	VERSION = dio->version;
	call RPLOF.resetRank();
        dbg("RPLRank","RPLRank: nodeRank = Infinite, resetValid()\n");
	nodeRank = INFINITE_RANK;
	minRank = INFINITE_RANK;
	//desiredParent = MAX_PARENT;
	resetValid();
	newDodag = TRUE;
      } else { // it depends
        //printf("MOVE TO NEW DODAG %d %d\n",compare_ipv6(&DODAGID, &DODAG_MAX), compare_ipv6(&DODAGID, &rDODAGID));
	newDodag = TRUE;
      }
/* printf_dbg("Wo isser denn 6 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
    } else if (compare_ipv6(&DODAGID, &DODAG_MAX)) { //not belong to a DODAG yet
      //      printf("TOTALLY NEW DODAG \n");

      dbg("MRHOF","TOTALLY NEW DODAG\n");
      Prf = tempPrf;
      memcpy_rpl((uint8_t*)&DODAGID, (uint8_t*)&rDODAGID, sizeof(struct in6_addr));
      parentNum = 0;
/* printf_dbg("Wo isser denn 7 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
      VERSION = dio->version;
      call RPLOF.resetRank();
      dbg("RPLRank","RPLRank: totally new dodag, nodeRank = Infinite, resetValid\n");
      nodeRank = INFINITE_RANK;
      minRank = INFINITE_RANK;
      //desiredParent = MAX_PARENT;
      newDodag = TRUE;
      resetValid();
/* printf_dbg("Wo isser denn 8 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
    } else {
/* printf_dbg("Wo isser denn 8 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
 // same DODAG
      //printf("FROM SAME DODAG \n");
      //Prf = tempPrf; // update prf
    }

    /////////////////////////////Collect data from DIOs/////////////////////////////////
    trackLength -= sizeof(struct dio_base_t);
    newPoint = (uint8_t*)(struct dio_base_t*)(dio + 1);
    dio_body = (struct dio_body_t*) newPoint;

    METRICID = 0;
    OCP = 0;

    // SDH : TODO : make some #defs for DODAG constants
/* printf_dbg("Wo isser denn 9 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
    if (dio_body->type == 2) { // this is metric

      trackLength -= sizeof(struct dio_body_t);

      newPoint = (uint8_t*)(struct dio_body_t*)(dio_body + 1);
      dio_metric_header = (struct dio_metric_header_t*) newPoint;
      trackLength -= sizeof(struct dio_metric_header_t);
/* printf_dbg("Wo isser denn 10 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
      if (dio_metric_header->routing_obj_type) {
	// etx metric
        // SDH : double cast
	// newPoint = (uint8_t*)(struct dio_metric_header_t*)(dio_metric_header + 1);
        newPoint = (uint8_t*)(dio_metric_header + 1);
	dio_etx = (struct dio_etx_t*)newPoint;
	trackLength -= sizeof(struct dio_etx_t);
	etx = dio_etx->etx;
	//printf("ETX RECV %d \n", etx);
	METRICID = 7;
	newPoint = (uint8_t*)(struct dio_etx_t*)(dio_etx + 1);
/* printf_dbg("Wo isser denn 11 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
      }
    }else{
      etx = pParentRank*divideRank;
      //printf("No ETX %d \n", dio_body->type);
    }
/* printf_dbg("Wo isser denn 12 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
    /* SDH : what is type 3? */
    dio_prefix = (struct dio_prefix_t*) newPoint;

    if (trackLength > 0 && dio_prefix->type == 3) {
/* printf_dbg("Wo isser denn 13 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
      trackLength -= sizeof(struct dio_prefix_t);
      if (ignore == FALSE){
        /* SDH : this will be a call to NeighborDiscovery */
        /* although we might want to make a PrefixManager component... */
	// New Prefix!!!!
	// TODO: Save prefix somewhere and make it a searchable command
      }
    }
/* printf_dbg("Wo isser denn 14 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
    /* SDH : type 4 is a configuration header. */
    dio_dodag_config = (struct dio_dodag_config_t*) newPoint;

    //printf("%d %d %d %d %d \n", trackLength, METRICID, dio_body->type, dio_prefix->type, dio_dodag_config->type);

    if (trackLength > 0 && dio_dodag_config->type == 4) {
      // this is configuration header
      trackLength -= sizeof(struct dio_dodag_config_t);
/* printf_dbg("Wo isser denn 15 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
      //printf(" > %d %d %d %d %d \n", trackLength, METRICID, dio_dodag_config->type, ignore, dio_dodag_config->ocp);

      if (ignore == FALSE) {

	OCP = dio_dodag_config->ocp;

	MAX_RANK_INCREASE = dio_dodag_config->MaxRankInc;
	//MIN_HOP_RANK_INCREASE = dio_dodag_config->MinHopRankInc;
/* printf_dbg("Wo isser denn 16 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */

	call RouteInfo.setDODAGConfig(dio_dodag_config->DIOIntDoubl, 
                                      dio_dodag_config->DIOIntMin, 
				      dio_dodag_config->DIORedun, 
                                      dio_dodag_config->MaxRankInc, 
                                      dio_dodag_config->MinHopRankInc);
	call RPLOF.setMinHopRankIncrease(dio_dodag_config->MinHopRankInc);
      }
    }

    ///////////////////////////////////////////////////////////////////////////////////

    printf("PR %d NR %d OCP %d MID %d \n", pParentRank, nodeRank, OCP, METRICID);

    // temporaily keep the parent information first
    memcpy_rpl((uint8_t*)&tempParent.parentIP, (uint8_t*)&iph->ip6_src, sizeof(struct in6_addr)); //may be not right!!!
    tempParent.rank = pParentRank;
    tempParent.etx_hop = INIT_ETX;
    tempParent.valid = TRUE;
    tempParent.etx = etx;
    if((!call RPLOF.objectSupported(METRICID) || !call RPLOF.OCP(OCP)) && parentNum == 0){
      // either I dont know the metric object or I don't support the OF
      printf("support the metric? %d support the OF? %d parent number = %d\n",call RPLOF.objectSupported(METRICID), call RPLOF.OCP(OCP), parentNum);
      insertParent(tempParent);
      call RPLOF.recomputeRoutes();
      //getNewRank(); no need to compute routes when I am going to stay as a leaf!
      dbg("RPLRank","RPLRank: recompute Route 2 nodeRank = Infinite\n");
      nodeRank = INFINITE_RANK;
      leafState = TRUE;
      return;
    }

    if ((parentIndex = getParent(&iph->ip6_src)) != MAX_PARENT) { 
      // parent already there and the rank is useful

      printf("HOW many parents ? %d %d \n", parentNum, newDodag);
/* printf_dbg("Status Rank:33 %i vor Reset \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
      if(newDodag){
	// old parent has to move to a new DODAG now
	if (parentNum != 0) {
printf_dbg("Status Rank:9 %i vor Reset \n",call RPLRankInfo.getRank(&ADDR_MY_IP));
	  //chooseDesired();
          dbg("RPLRank","RPLRank: RecomputeRoutes3\n");
	  call RPLOF.recomputeRoutes(); // we do this to make sure that this parent is still the best and it is worth moving

	  myParent = getParent(call RPLOF.getParent());

	  if (!compareParent(parentSet[myParent], tempParent)) {
	    // the new dodag is not from my desired parent node
	    Prf = tempPrf;
	    memcpy_rpl((uint8_t*)&DODAGID, (uint8_t*)&rDODAGID, sizeof(struct in6_addr));
	    parentNum = 0;
	    VERSION = dio->version;
            dbg("RPLRank","RPLRank: New DODAG is not my desired parent node, resetValid\n");
	    resetValid();
	    insertParent(tempParent);
            dbg("RPLRank","RPLRank: RecomputeRoutes4\n");
	    call RPLOF.recomputeRoutes();
printf_dbg("Status Rank:99 %i vor Reset \n",call RPLRankInfo.getRank(&ADDR_MY_IP));
	    getNewRank();
	  } else {
	    // I have a better node in the current DODAG so I am not moving!
            printf_dbg("Status Rank:999 %i vor Reset \n",call RPLRankInfo.getRank(&ADDR_MY_IP));
            dbg("RPLRank","RPLRank: RecomputeRoutes5\n");
	    call RPLOF.recomputeRoutes();
	    getNewRank();
	    ignore = TRUE;
	  }
	} else {
          dbg("MRHOF","parentNum = 0,resetValid\n");
	  // not likely to happen but this is a new DODAG...
	  Prf = tempPrf;
	  memcpy_rpl((uint8_t*)&DODAGID, (uint8_t*)&rDODAGID, sizeof(struct in6_addr));
	  parentNum = 0;
	  VERSION = dio->version;
	  resetValid();
	  insertParent(tempParent);
          dbg("RPLRank","RPLRank: RecomputeRoutes6\n");
	  call RPLOF.recomputeRoutes();
	  getNewRank();
	}

      }else{
        //printf("old DODAG\n");
        dbg("RPLRank","RPLRank: old DODAG\n");
	// this DIO is just from a parent that I know already, update and re-evaluate
        printf("known parent -- update\n");
        printf("RPLRank: parentNode = %u \n",  (uint8_t)htons(parentSet[parentIndex].parentIP.s6_addr16[7]));
	parentSet[parentIndex].rank = pParentRank; //update rank
	parentSet[parentIndex].etx = etx;
        dbg("RPLRank","RPLRank: RecomputeRoutes7\n");
	call RPLOF.recomputeRoutes();
	getNewRank();
	ignore = TRUE;
      }

    }else{

/* printf_dbg("Wo isser denn 21 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
      // this parent is not in my routing table

      //      printf("HOW many parents? %d \n", parentNum);

      if(parentNum > MAX_PARENT) // ><><><><><>< how do i share the parent count?
	return;

      // at this point know that its a meaningful packet from a new node and we have space to store

      //printf("New parent %d %d %d\n", ntohs(iph->ip6_src.s6_addr16[7]), tempParent.etx_hop, parentNum);

      if(newDodag){
/* printf_dbg("Wo isser denn 22 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
	// not only is this parent new but we have to move to a new DODAG now
	printf("New DODAG \n");
	if (parentNum != 0) {
          printf("RPLRank:parentNum!=0\n");
	  call RPLOF.recomputeRoutes(); // make sure that I don't have an alternative path on this DODAG
	  myParent = getParent(call RPLOF.getParent());
	  if (!compareParent(parentSet[myParent], tempParent)) {
	    // parentIndex == desiredParent, parentNum != 0, !compareParent
	    //printf("changing DODAG\n");
	    Prf = tempPrf;
	    memcpy_rpl((uint8_t*)&DODAGID, (uint8_t*)&rDODAGID, sizeof(struct in6_addr));
	    parentNum = 0;
	    VERSION = dio->version;
            dbg("RPLRank","RPLRank: resetValid, recomputeRoutes9\n");
	    resetValid();
/* printf_dbg("Wo isser denn 23 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
	    insertParent(tempParent);
	    call RPLOF.recomputeRoutes();
	    getNewRank();
	  } else {
	    //do nothing
	    ignore = TRUE;
/* printf_dbg("Wo isser denn 24 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP)); */
	  }
	} else {
          dbg("RPLRank","PRLRank: parentNum =0, resetValid()\n");
	  // This is the first DODAG I am registering ... or the once before are all goners already
	  //printf("First DODAG\n");
	  Prf = tempPrf;
	  memcpy_rpl((uint8_t*)&DODAGID, (uint8_t*)&rDODAGID, sizeof(struct in6_addr));
	  parentNum = 0;
	  VERSION = dio->version;
	  resetValid();
	  insertParent(tempParent);
          //printf("Wo isser denn End 1 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP));
          dbg("RPLRank","RPLRank: recomputeRoutes 10\n");
	  call RPLOF.recomputeRoutes();
          //printf_dbg("Wo isser denn End 2 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP));
          getNewRank();//Hier geht auseinander node 2 und node 3
 //printf_dbg("Wo isser denn End 3 %i \n",call RPLRankInfo.getRank(&ADDR_MY_IP));
	}
      }else{
	// its a new parent from the current DODAG .. so no need for DODAG configuarion just insert
        dbg("RPLRank","RPLRank: Same DODAG %d \n", parentNum);
	insertParent(tempParent);
        dbg("RPLRank","RPLRank: recomputeRoutes 11\n");
        call RPLOF.recomputeRoutes(); 
        preRank = nodeRank;
        getNewRank();
      }
    }
  }

  /* 
   * Processing for incomming DIO, DAO, and DIS messages.
   *
   * SDH : we should not snoop on these from the forwarding engine;
   * instead we now go through the IPProtocols component to receive
   * them the normal way through the ICMP stack.  Things like
   * verifying the checksum can go in there.
   *
   */
  event void IP_DIO.recv(struct ip6_hdr *iph, void *payload, 
                         size_t len, struct ip6_metadata *meta){
    struct dio_base_t *dio;
    struct in6_addr ADDR_MY_IP;
    int i;
    dio = (struct dio_base_t *) payload;
    call IPAddress.getGlobalAddr(&ADDR_MY_IP);
    dbg("RPLRank","RPLRank:IP_DIO.recv: MY_IP = ");
    printf_in6addr_dbg(&ADDR_MY_IP);

    if (!m_running) return;

    dbg("RPLRank","IP_DIO.recv: print receiving payload: ");    
    for (i=0;i<sizeof(struct dio_base_t);i++){
      dbg_clear("RPLRank","%x",((uint8_t*)payload)[i]);
    }
    dbg_clear("RPLRank","\n");

    if(nodeRank != ROOT_RANK && dio->dagRank != 0xFFFF)
      parseDIO(iph, dio);

    // evict parent if the node is advertizing 0xFFFF;
    if(dio->dagRank == 0xFFFF && getParent(&iph->ip6_src) != MAX_PARENT){
      printf("DIO advertizing rank 0xFFFF, Jetzt Rank: %i \n",
                 call RPLRankInfo.getRank(&ADDR_MY_IP));
      evictParent(getParent(&iph->ip6_src));
    }
    printf_dbg("Status vor DAG akzeptiert 2 in RankP Jetzt Rank: %i \n",
               call RPLRankInfo.getRank(&ADDR_MY_IP));

    //leafState = FALSE;
    if (nodeRank > dio->dagRank || dio->dagRank == INFINITE_RANK) {
      if (!ignore) {
        /* SDH : where did this go? */
        printf_dbg("Status vor DAG akzeptiert 3 in RankP Jetzt Rank: %i \n",
                   call RPLRankInfo.getRank(&ADDR_MY_IP));
        signal IP_DIO_Filter.recv(iph, payload, len, meta);
      }
      ignore = FALSE;
    }
  }

  command error_t IP_DIO_Filter.send(struct ip6_packet *msg) {
    return call IP_DIO.send(msg);
  }

  event void IPAddress.changed(bool global_valid) {}
}
