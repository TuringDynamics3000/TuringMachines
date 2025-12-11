import MobileLayout from "../components/MobileLayout";

export default function ManualReview() {
  return (
    <MobileLayout>
      <div className="text-center">
        <div className="mb-6">
          <svg className="mx-auto h-24 w-24 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h2 className="text-3xl font-bold mb-2 text-blue-600">Identity Under Review</h2>
        <p className="text-lg text-gray-700 mb-8">Our team is reviewing your submission.</p>
        <div className="card text-left">
          <p className="text-sm text-gray-600 mb-4">
            Your identity verification requires manual review by our compliance team.
          </p>
          <div className="space-y-2 text-sm">
            <p><strong>Review Time:</strong> 1-2 business days</p>
            <p><strong>Reference ID:</strong> #TUR-{Math.random().toString(36).substr(2, 9).toUpperCase()}</p>
          </div>
          <p className="text-sm text-gray-600 mt-4">
            We will notify you via email once the review is complete.
          </p>
        </div>
        <button className="btn mt-8" onClick={() => window.location.href = "/"}>Done</button>
      </div>
    </MobileLayout>
  );
}
