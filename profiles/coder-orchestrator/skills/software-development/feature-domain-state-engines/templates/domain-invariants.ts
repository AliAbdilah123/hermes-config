export const money=(digits:string,multiplier=1)=>{const n=Number(digits.replace(/[^0-9]/g,""));if(!Number.isSafeInteger(n))throw Error("invalid amount");return n*multiplier};
export function collectUnique<T>(root:T,children:(x:T)=>T[],ids:(x:T)=>string[]){const out=new Set<string>();const walk=(n:T)=>{ids(n).forEach(x=>out.add(x));children(n).forEach(walk)};walk(root);return [...out]}
export function splitEdge<T extends {from:string;to:string}>(edges:T[],edge:T,node:string):T[]{return [...edges.filter(e=>e!==edge),{...edge,to:node},{...edge,from:node}]}
