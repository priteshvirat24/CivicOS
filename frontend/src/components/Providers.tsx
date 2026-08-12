"use client";

import { SWRConfig } from "swr";
import { fetcher } from "@/utils/fetcher";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig 
      value={{ 
        fetcher,
        revalidateOnFocus: false,
        dedupingInterval: 5000, 
      }}
    >
      {children}
    </SWRConfig>
  );
}
