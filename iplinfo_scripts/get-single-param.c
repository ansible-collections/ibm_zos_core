#include <stdio.h>

/* --- Map PSA ------------------------------------------------------ */
struct psa {
    char psastuff[16];                  /* 16 bytes before CVT Ptr     */
    struct cvt *psacvt;
    /* Ignore the rest of the PSA */
};
/* --- Cut down CVT Structure --------------------------------------- */
struct cvt {
    char cvtstuff[140];                 /* 140 bytes before ptr        */
    struct ecvt *cvtecvt;               /* Ptr to ECVT                 */
    /* Ignore the rest of the CVT */
};
/* --- Cut down ECVT Structure -------------------------------------- */
struct ecvt {
    char ecvtstuff[392];                /* 392 bytes before IPA ptr    */
    struct ipa *ecvtipa;                  /* Ptr to IPA                  */
    /* Ignore the rest of the ECVT */
};

struct ipa {
    char ipastuff[20];
    char IPALOADS[2];  // offset 20 (14)
    char _0_ipastuff[26];
    char IPALPDSN[44];  // offset 48 (30)
    char IPALPDDV[4];   // offset 92 (5c)
};

struct ipa* my_ipa() {

    struct psa* psa = 0;
    struct cvt* cvt = psa->psacvt;
    struct ecvt* ecvt = (cvt->cvtecvt);
    struct ipa* ipa = (ecvt->ecvtipa);
    return ipa;
}

const char* getParam(){
    return my_ipa()->IPALPDSN;
}

int main(){
    printf("%s\n", getParam());
}