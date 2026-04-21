"use client";
import api from "@/lib/api";
import React from "react";

const TestPage = () => {
  const testRequest = async () => {
    try {
      const res = await api.get("/auth/me");
      console.log(res);
      alert(`Response: ${JSON.stringify(res.data)}`);
    } catch (error) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div>
      <button
        className="border cursor-pointer bg-zinc-900 text-white rounded-md px-8 py-4"
        onClick={testRequest}
      >
        Send the test req to / to the backend
      </button>
    </div>
  );
};

export default TestPage;
