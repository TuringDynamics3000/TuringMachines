import MobileLayout from "../components/MobileLayout";

export default function Rejected() {
  return (
    <MobileLayout>
      <div className="text-center">
        <div className="mb-6">
          <svg className="mx-auto h-24 w-24 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold mb-2 text-red-600">Verification Failed</h2>
        <p className="text-lg text-gray-700 mb-8">We were unable to verify your identity at this time.</p>
        <div className="card text-left">
          <p className="text-sm text-gray-600 mb-4">
            Your identity verification was not successful due to one or more of the following reasons:
          </p>
          <ul className="space-y-2 text-sm text-gray-700">
            <li>• Document quality issues</li>
            <li>• Information mismatch</li>
            <li>• Risk assessment concerns</li>
          </ul>
          <p className="text-sm text-gray-600 mt-4">
            You may retry the verification process or contact our support team for assistance.
          </p>
        </div>
        <button className="btn mt-8" onClick={() => window.location.href = "/"}>Try Again</button>
        <button className="btn-secondary mt-3">Contact Support</button>
      </div>
    </MobileLayout>
  );
}
