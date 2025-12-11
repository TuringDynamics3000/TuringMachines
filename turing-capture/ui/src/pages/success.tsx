import MobileLayout from "../components/MobileLayout";
import { useEffect } from "react";
import { clearSession } from "../lib/session";

export default function Success() {
  useEffect(() => {
    clearSession();
  }, []);

  return (
    <MobileLayout>
      <div className="text-center">
        <div className="mb-6">
          <svg className="mx-auto h-24 w-24 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold mb-2 text-green-600">Identity Verified</h2>
        <p className="text-lg text-gray-700 mb-8">Your identity has been successfully verified.</p>
        <div className="card space-y-3 text-left">
          <div className="flex items-center">
            <span className="text-green-500 mr-3">✓</span>
            <span>Document verified</span>
          </div>
          <div className="flex items-center">
            <span className="text-green-500 mr-3">✓</span>
            <span>Selfie matched</span>
          </div>
          <div className="flex items-center">
            <span className="text-green-500 mr-3">✓</span>
            <span>Risk assessment passed</span>
          </div>
        </div>
        <button className="btn mt-8" onClick={() => window.location.href = "/"}>Done</button>
      </div>
    </MobileLayout>
  );
}
