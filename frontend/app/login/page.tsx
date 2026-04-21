// "use client";
// import { useAuth } from "@/context/AuthContext";
// import { useState } from "react";

// export default function Login() {
//   const { login } = useAuth();
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();
//     await login(email, password);
//     window.location.href = "/"; // go to dashboard
//   };

//   return (
//     <form onSubmit={handleSubmit}>
//       <input
//         type="email"
//         value={email}
//         onChange={(e) => setEmail(e.target.value)}
//         placeholder="Email"
//         required
//       />
//       <input
//         type="password"
//         value={password}
//         onChange={(e) => setPassword(e.target.value)}
//         placeholder="Password"
//         required
//       />
//       <button type="submit">Login</button>
//     </form>
//   );
// }

"use client";
import { authClient } from "@/lib/auth-client";

// Example Sign-In Function
const handleSignIn = async () => {
  const { data, error } = await authClient.signIn.email(
    {
      email: "test@example.com",
      password: "password123",
      rememberMe: true,
    },
    {
      onError: (ctx) => alert(ctx.error.message),
    },
  );
};

export default function Login() {
  return (
    <div>
      <h1>Login</h1>
      <button
        className="border bg-zinc-900 text-white rounded-md px-8 py-4"
        onClick={handleSignIn}
      >
        Sign In with Email
      </button>
    </div>
  );
}
