"use client";
import { authClient } from "@/lib/auth-client";

// Example Sign-Up Function
const handleSignUp = async () => {
  const { data, error } = await authClient.signUp.email(
    {
      name: "Abdullah Qureshi",
      email: "abdullah@gmail.com",
      password: "password",
      callbackURL: "/dashboard",
    },
    {
      onError: (ctx) => alert(ctx.error.message),
    },
  );
};

export default function Register() {
  return (
    <div>
      <h1>Register</h1>
      <button
        className="border bg-zinc-900 text-white rounded-md px-8 py-4"
        onClick={handleSignUp}
      >
        Sign Up with Email
      </button>
    </div>
  );
}
