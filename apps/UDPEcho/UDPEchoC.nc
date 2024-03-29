/*
 * Copyright (c) 2008 The Regents of the University  of California.
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

#include <lib6lowpan/6lowpan.h>
#include "TestMessage.h"
configuration UDPEchoC {

} implementation {
  components MainC, LedsC;
  components UDPEchoP;

  UDPEchoP.Boot -> MainC;
  UDPEchoP.Leds -> LedsC;

  components new TimerMilliC() as StatusTimer;
  components new TimerMilliC() as DelayTimer;
  components IPStackC;

  UDPEchoP.RadioControl ->  IPStackC;
  components new UdpSocketC() as UDPSend,
    new UdpSocketC() as UDPReceive;

  UDPEchoP.UDPSend -> UDPSend;
  UDPEchoP.UDPReceive -> UDPReceive;

  UDPEchoP.StatusTimer -> StatusTimer;
  UDPEchoP.DelayTimer -> DelayTimer;

  components UdpC, IPDispatchC;
  UDPEchoP.IPStats -> IPDispatchC;
  UDPEchoP.UDPStats -> UdpC;

#ifdef TOSSIM
#ifdef RPL_ROUTING
  components RPLRoutingC;
  UDPEchoP.RootControl -> RPLRoutingC;
#endif
#endif

  components RandomC;
  UDPEchoP.Random -> RandomC;

  // UDP shell on port 2000
  components UDPShellC;

  // prints the routing table
  components RouteCmdC;
#ifndef  IN6_PREFIX
  components DhcpCmdC;
#endif
}
