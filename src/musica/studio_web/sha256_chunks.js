/* G3B1B: bounded incremental SHA-256 for a user-picked Blob/File.
 * Only one 1MiB slice is resident; never file.arrayBuffer() for full WAV.
 * Browser-only, derived transport state; never an authority for Project revisions.
 */
(() => {
  "use strict";
  const K = new Uint32Array([
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
  ]);
  const rotate = (x, n) => (x >>> n) | (x << (32 - n));

  class IncrementalSha256 {
    constructor() {
      this.state = new Uint32Array([
        0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,
        0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19
      ]);
      this.block = new Uint8Array(64);
      this.used = 0;
      this.byteCount = 0;
    }
    compress(data) {
      const w = new Uint32Array(64);
      for (let i=0;i<16;i++) {
        const j=i*4;
        w[i]=((data[j]<<24)|(data[j+1]<<16)|(data[j+2]<<8)|data[j+3])>>>0;
      }
      for (let i=16;i<64;i++) {
        const x=w[i-15], y=w[i-2];
        const a=rotate(x,7)^rotate(x,18)^(x>>>3);
        const b=rotate(y,17)^rotate(y,19)^(y>>>10);
        w[i]=(w[i-16]+a+w[i-7]+b)>>>0;
      }
      let [a,b,c,d,e,f,g,h] = this.state;
      for (let i=0;i<64;i++) {
        const s1=rotate(e,6)^rotate(e,11)^rotate(e,25);
        const choose=(e&f)^(~e&g);
        const t1=(h+s1+choose+K[i]+w[i])>>>0;
        const s0=rotate(a,2)^rotate(a,13)^rotate(a,22);
        const majority=(a&b)^(a&c)^(b&c);
        const t2=(s0+majority)>>>0;
        h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=b;b=a;a=(t1+t2)>>>0;
      }
      const next=[a,b,c,d,e,f,g,h];
      for(let i=0;i<8;i++)this.state[i]=(this.state[i]+next[i])>>>0;
    }
    update(data) {
      if (!(data instanceof Uint8Array))throw new Error("Expected Uint8Array chunk");
      this.byteCount+=data.length;
      if (!Number.isSafeInteger(this.byteCount))throw new Error("SHA-256 length overflow");
      let at=0;
      while(at<data.length) {
        const count=Math.min(64-this.used,data.length-at);
        this.block.set(data.subarray(at,at+count),this.used);
        this.used+=count;at+=count;
        if(this.used===64){this.compress(this.block);this.used=0;}
      }
    }
    digestHex() {
      const original=this.byteCount;
      const padBytes=(this.used<56?56:120)-this.used;
      const padding=new Uint8Array(padBytes);
      padding[0]=0x80;
      this.update(padding);
      const trailer=new Uint8Array(8);
      let bits=BigInt(original)*8n;
      for(let i=7;i>=0;i--){trailer[i]=Number(bits&255n);bits>>=8n;}
      this.update(trailer);
      return Array.from(this.state).map(x=>x.toString(16).padStart(8,"0")).join("");
    }
  }

  async function hashFileSlices(file, progress, isCancelled) {
    const max=64*1024*1024, step=1024*1024;
    if (!file || !Number.isSafeInteger(file.size) || file.size<44 || file.size>max)
      throw new Error("WAV length must be 44 bytes through 64 MiB");
    const hasher=new IncrementalSha256();
    for(let offset=0;offset<file.size;offset+=step){
      if(isCancelled?.())throw new Error("WAV hashing cancelled");
      const end=Math.min(offset+step,file.size);
      hasher.update(new Uint8Array(await file.slice(offset,end).arrayBuffer()));
      if(progress)progress(end,file.size);
    }
    if(isCancelled?.())throw new Error("WAV hashing cancelled");
    return hasher.digestHex();
  }
  window.MUSICA_SHA256_FILE = {hashFileSlices, IncrementalSha256};
})();
