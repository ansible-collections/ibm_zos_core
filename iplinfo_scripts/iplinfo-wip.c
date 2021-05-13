#include <stdio.h>

struct psa {
    char psastuff[16];                  /* 16 bytes before CVT Ptr     */
    struct cvt *psacvt;
};
struct cvt {
    char cvtstuff[140];                 /* 140 bytes before ptr        */
    struct ecvt *cvtecvt;               /* Ptr to ECVT                 */
    char _buf[184];                       /* offset 328 */
    struct ext2 *cvtext2;                /* Ptr to EXT2 */
};
struct ecvt {
    char ecvtstuff[392];                /* 392 bytes before IPA ptr    */
    struct ipa *ecvtipa;                  /* Ptr to IPA                  */
};

struct ipa {
    char ipastuff[20];
    char IPALOADS[2];  // offset 20 (14)
    char _0_ipastuff[26];
    char IPALPDSN[44];  // offset 48 (30)
    char IPALPDDV[4];   // offset 92 (5c)
    // char _1_ipastuff[256];
    // char IPASXNAM[8]; // offset 352 (160)
};

struct ext2 {
    char _buf_1[6];
    char a[2]; //iodf
};

typedef struct {
    char loadds[2]; // load data set
    char parmlibdsn[44]; // parmlib data set name name
} iplinfo;

struct ext2* my_ext2() {
    struct psa* psa = 0;
    struct cvt* cvt = psa->psacvt;
    struct ext2* ext2 = (cvt->cvtext2);
    return ext2;
}

struct ipa* get_ipa() {
    struct psa* psa = 0;
    struct cvt* cvt = psa->psacvt;
    struct ecvt* ecvt = (cvt->cvtecvt);
    struct ipa* ipa = (ecvt->ecvtipa);
    return ipa;
}

const char* getThingy(){
    // return get_ipa()->IPAPLVOL;
    return my_ext2()->a;
}

const char* getIPALOADS(iplinfo* i){

    char str[1+sizeof(i->loadds)]; // cannot initialize variable length array
    memset(str, 0, sizeof(str)); // zero out string
    memcpy(str, i->loadds, sizeof(i->loadds)); // copy param as nul-terminated string
    return str;
}
const char* getIPALPDSN(){
    return get_ipa()->IPALPDSN;
}
const char* getIPALPDDV(){
    return get_ipa()->IPALPDDV;
}
// const char* getIPASXNAM(){
//     return get_ipa()->IPASXNAM;
// }

struct iplinfo* get_iplinfo(){
    struct iplinfo _iplinfo;
    strcpy(_iplinfo.loadds, getIPALOADS());
    return &_iplinfo;
}

const char* printIplinfoJSON(struct iplinfo* target ){
    printf("{ load-ds : %s }", target->loadds );
}

int main(){
}

/*

create string/print functions for JSON outputm, Human readable output, and something else. Target is "USED LOADEC IN SYS1.PARMLIB ON 00742"

-- missing piece is iodf  -- iodf card image? ecvt at offset 96.

take that to zoau utility integration

*/