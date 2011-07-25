#include <stdint.h>

#include "nwbyte_sim.h"

uint32_t ntohl(uint32_t i) {
  uint16_t lo = (uint16_t)i;
  uint16_t hi = (uint16_t)(i >> 16);
  lo = (lo << 8) | (lo >> 8);
  hi = (hi << 8) | (hi >> 8);
  return (((uint32_t)lo) << 16) | ((uint32_t)hi);
}

uint8_t *ip_memcpy(uint8_t *dst0, const uint8_t *src0, uint16_t len) {
  uint8_t *dst = (uint8_t *) dst0;
  uint8_t *src = (uint8_t *) src0;
  uint8_t *ret = dst0;

  for (; len > 0; len--)
    *dst++ = *src++;

  return ret;
}
