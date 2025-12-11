import MobileLayout from "../components/MobileLayout";

export default function StepUp() {
  return (
    <MobileLayout>
      <div className="text-center">
        <div className="mb-6">
          <svg className="mx-auto h-24 w-24 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold mb-2 text-yellow-600">Additional Verification Required</h2>
        <p className="text-lg text-gray-700 mb-8">We need a bit more information to verify your identity.</p>
        <div className="card text-left">
          <p className="text-sm text-gray-600 mb-4">
            Based on our risk assessment, we require additional verification steps:
          </p>
          <ul className="space-y-2 text-sm">
            <li>• Phone number verification</li>
            <li>• Address confirmation</li>
            <li>• Additional document upload</li>
          </ul>
        </div>
        <button className="btn mt-8">Continue Verification</button>
        <button className="btn-secondary mt-3">Contact Support</button>
      </div>
    </MobileLayout>
  );
}
