// lib/auth-client.ts
import { createAuthClient } from "better-auth/client";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: "http://localhost:3000",   // your Next.js URL
  plugins: [jwtClient()],
});