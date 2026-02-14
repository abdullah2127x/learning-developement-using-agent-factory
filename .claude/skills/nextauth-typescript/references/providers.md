# Providers

## OAuth Providers

### GitHub

```typescript
import GitHub from "next-auth/providers/github";

// Auto-detect (uses AUTH_GITHUB_ID + AUTH_GITHUB_SECRET)
providers: [GitHub]

// Manual config
providers: [
  GitHub({
    clientId: process.env.AUTH_GITHUB_ID,
    clientSecret: process.env.AUTH_GITHUB_SECRET,
  }),
]
```

### Google

```typescript
import Google from "next-auth/providers/google";

// Auto-detect (AUTH_GOOGLE_ID + AUTH_GOOGLE_SECRET)
providers: [Google]

// With specific scopes
providers: [
  Google({
    authorization: {
      params: {
        scope: "openid email profile",
        prompt: "consent",
        access_type: "offline",
        response_type: "code",
      },
    },
  }),
]
```

**Google Console setup**:
- Authorized redirect URI: `https://your-domain.com/api/auth/callback/google`
- For local dev: `http://localhost:3000/api/auth/callback/google`

### Discord

```typescript
import Discord from "next-auth/providers/discord";
providers: [Discord]
// AUTH_DISCORD_ID + AUTH_DISCORD_SECRET
```

### Apple

```typescript
import Apple from "next-auth/providers/apple";

providers: [
  Apple({
    clientId: process.env.AUTH_APPLE_ID,
    clientSecret: process.env.AUTH_APPLE_SECRET,
  }),
]
```

### Custom OAuth Provider

```typescript
import type { OAuthConfig } from "next-auth/providers";

interface CustomProfile {
  id: string;
  login: string;
  email: string;
  avatar_url: string;
}

const CustomProvider: OAuthConfig<CustomProfile> = {
  id: "custom",
  name: "Custom Provider",
  type: "oauth",
  authorization: "https://provider.com/oauth/authorize",
  token: "https://provider.com/oauth/token",
  userinfo: "https://provider.com/api/user",
  profile(profile) {
    return {
      id: profile.id,
      name: profile.login,
      email: profile.email,
      image: profile.avatar_url,
    };
  },
};
```

## Credentials Provider

For email/password authentication. **Requires your own user validation logic.**

### Basic Setup

```typescript
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcryptjs";

providers: [
  Credentials({
    name: "credentials",
    credentials: {
      email: { label: "Email", type: "email" },
      password: { label: "Password", type: "password" },
    },
    async authorize(credentials) {
      if (!credentials?.email || !credentials?.password) return null;

      const user = await db.user.findUnique({
        where: { email: credentials.email as string },
      });

      if (!user || !user.hashedPassword) return null;

      const isValid = await bcrypt.compare(
        credentials.password as string,
        user.hashedPassword
      );

      if (!isValid) return null;

      return {
        id: user.id,
        name: user.name,
        email: user.email,
        image: user.image,
      };
    },
  }),
]
```

### With Zod Validation

```typescript
import { z } from "zod";
import Credentials from "next-auth/providers/credentials";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

providers: [
  Credentials({
    credentials: {
      email: { label: "Email", type: "email" },
      password: { label: "Password", type: "password" },
    },
    async authorize(credentials) {
      const parsed = loginSchema.safeParse(credentials);
      if (!parsed.success) return null;

      const { email, password } = parsed.data;
      const user = await getUserByEmail(email);
      if (!user) return null;

      const isValid = await verifyPassword(password, user.hashedPassword);
      if (!isValid) return null;

      return { id: user.id, name: user.name, email: user.email };
    },
  }),
]
```

### Important Credentials Limitations

- **No database sessions** with Credentials by default (JWT only)
- **No automatic account linking** — must handle manually
- Auth.js team recommends OAuth or Email providers over Credentials
- You handle user creation/registration yourself (outside Auth.js)

## Email Provider (Magic Links)

Requires a database adapter.

```typescript
import Email from "next-auth/providers/email";

providers: [
  Email({
    server: {
      host: process.env.EMAIL_SERVER_HOST,
      port: Number(process.env.EMAIL_SERVER_PORT),
      auth: {
        user: process.env.EMAIL_SERVER_USER,
        pass: process.env.EMAIL_SERVER_PASSWORD,
      },
    },
    from: process.env.EMAIL_FROM,
  }),
]
```

### With Resend

```typescript
import Resend from "next-auth/providers/resend";

providers: [
  Resend({
    from: "noreply@yourdomain.com",
    // AUTH_RESEND_KEY env var auto-detected
  }),
]
```

## Multiple Providers

```typescript
import NextAuth from "next-auth";
import GitHub from "next-auth/providers/github";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    GitHub,
    Google,
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      authorize: async (credentials) => {
        // ... validation logic
      },
    }),
  ],
});
```

### Custom Sign-In Page with Multiple Providers

```typescript
// app/auth/signin/page.tsx
import { signIn, providerMap } from "@/auth";

export default async function SignInPage() {
  return (
    <div>
      {Object.values(providerMap).map((provider) => (
        <form
          key={provider.id}
          action={async () => {
            "use server";
            await signIn(provider.id);
          }}
        >
          <button type="submit">Sign in with {provider.name}</button>
        </form>
      ))}
    </div>
  );
}
```

### Redirect After Sign In

```typescript
// Server Action with redirect
await signIn("github", { redirectTo: "/dashboard" });

// Client-side
import { signIn } from "next-auth/react";
signIn("github", { callbackUrl: "/dashboard" });
```

## Provider Profile Mapping

Override how profile data maps to user:

```typescript
GitHub({
  profile(profile) {
    return {
      id: profile.id.toString(),
      name: profile.name ?? profile.login,
      email: profile.email,
      image: profile.avatar_url,
      role: "user",  // Custom field
    };
  },
}),
```

## Available Built-in Providers

Auth.js supports 80+ providers. Common ones:
- **OAuth**: GitHub, Google, Discord, Apple, Twitter, Facebook, LinkedIn, Spotify, Twitch, Slack, Azure AD, Okta, Auth0, Keycloak, Cognito
- **Email**: Email, Resend, Sendgrid, Postmark, Nodemailer
- **Credentials**: Custom login form

Full list: https://authjs.dev/getting-started/providers
