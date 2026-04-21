// lib/auth.ts
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";   // ← Add this

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: true,                    // Neon requires SSL
});
console.log("the database url is:", process.env.DATABASE_URL!.slice(0, 20) + "..."); // for debugging
console.log("the better auth secret is:", process.env.BETTER_AUTH_SECRET!); // for debugging

export const auth = betterAuth({
  // database: {
  //   // Better Auth will use the same Neon DB as your backend
  //   url: process.env.DATABASE_URL!, // add this to your .env
  //   provider: "postgresql",
  // },

  database: pool,               // ← Use raw Pool instead of built-in
  // for sqlite (for local dev and testing), use this config instead:
  // database: {
  //   url: process.env.DATABASE_URL!, // add this to your .env
  //   provider: "sqlite",
  // },
  
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // you can turn on later
  },
  plugins: [
    jwt({
      // Better Auth uses EdDSA by default (asymmetric).
      jwt: {
        // algorithm: "HS256",
        secret: process.env.BETTER_AUTH_SECRET || "your-very-long-secret-here",
        expirationTime: "15m", // same as your access token
        definePayload: (session) => ({
          sub: session.user.id,
          email: session.user.email,
          role: session.user.role || "user",
        }),
      },
    }),
  ],
  //  plugins: [nextCookies()] 
  // Important for cross-origin (FastAPI on port 8000)
  trustedOrigins: ["http://localhost:8000"],
});
