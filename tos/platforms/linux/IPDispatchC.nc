/*
 * "Copyright (c) 2008 The Regents of the University  of California.
 * All rights reserved."
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
 */

/**
 * 
 *
 */
#include "IPDispatch.h"
#include "BlipStatistics.h"

configuration IPDispatchC {
  provides {
    interface SplitControl;
    interface IPLower;
    interface BlipStatistics<ip_statistics_t>;
  }
} implementation {
  
  
  /* IPDispatchP wiring -- fragment rassembly and lib6lowpan bindings */
  components IPDispatchP, IPAddressC;
  components MainC, IPStackC;

  SplitControl = IPDispatchP.SplitControl;
  IPLower = IPDispatchP;
  BlipStatistics    = IPDispatchP;

  IPDispatchP.IPAddress -> IPAddressC;
  IPDispatchP.Boot -> MainC;
  IPDispatchP.ForwardingTable -> IPStackC;
}
