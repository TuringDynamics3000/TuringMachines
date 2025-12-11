// TuringIdentity™ Adaptive Selfie + Passive Liveness Capture
// MediaPipe FaceMesh + Auto-Capture + Stripe-style UI

import { useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/router';
import MobileLayout from '../components/MobileLayout';
import CameraFeed from '../components/CameraFeed';
import AdaptiveGuidanceRing from '../components/AdaptiveGuidanceRing';
import { LivenessEngine, LivenessResult } from '../lib/LivenessEngine';
import { uploadSelfie } from '../lib/api';
import { submitSelfie } from '../lib/orchestrate';
import { getSession } from '../lib/session';
import { Results } from '@mediapipe/face_mesh';

export default function SelfieLivenessPage() {
  const router = useRouter();
  const [captured, setCaptured] = useState<string | null>(null);
  const [livenessResult, setLivenessResult] = useState<LivenessResult>({
    livenessScore: 0,
    blinkScore: 0,
    motionScore: 0,
    facePresent: false,
    faceCentered: false,
    faceSize: 0,
    landmarks: [],
    confidence: 0,
  });
  const [guidanceMessage, setGuidanceMessage] = useState('Position your face in the frame');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);

  const engineRef = useRef<LivenessEngine>(new LivenessEngine());
  const captureAttempted = useRef(false);

  const handleCameraResults = useCallback((results: Results) => {
    if (captureAttempted.current) return;

    const engine = engineRef.current;

    // Check if face landmarks are present
    if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
      const emptyResult: LivenessResult = {
        livenessScore: 0,
        blinkScore: 0,
        motionScore: 0,
        facePresent: false,
        faceCentered: false,
        faceSize: 0,
        landmarks: [],
        confidence: 0,
      };
      setLivenessResult(emptyResult);
      setGuidanceMessage(engine.getGuidanceMessage(emptyResult));
      return;
    }

    // Get first face landmarks
    const landmarks = results.multiFaceLandmarks[0];

    // Compute liveness
    const liveness = engine.computeLiveness(landmarks);
    setLivenessResult(liveness);

    // Update guidance message
    const message = engine.getGuidanceMessage(liveness);
    setGuidanceMessage(message);

    // Auto-capture when liveness is valid
    if (engine.isLivenessValid(liveness) && !captured) {
      captureAttempted.current = true;
      captureImage(results.image, liveness);
    }
  }, [captured]);

  const captureImage = async (image: HTMLVideoElement | HTMLImageElement, liveness: LivenessResult) => {
    try {
      // Create canvas to capture image
      const canvas = document.createElement('canvas');
      canvas.width = 480;
      canvas.height = 640;
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        throw new Error('Failed to get canvas context');
      }

      // Draw image (mirrored)
      ctx.save();
      ctx.scale(-1, 1);
      ctx.translate(-canvas.width, 0);
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      ctx.restore();

      // Convert to data URL
      const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
      setCaptured(dataUrl);

      // Upload to backend
      await uploadBiometrics(dataUrl, liveness);
    } catch (err) {
      console.error('Capture error:', err);
      setError('Failed to capture image. Please try again.');
      captureAttempted.current = false;
    }
  };

  const uploadBiometrics = async (imageDataUrl: string, liveness: LivenessResult) => {
    const session_id = getSession();
    if (!session_id) {
      setError('Session missing. Please start over.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Convert data URL to File
      const blob = await (await fetch(imageDataUrl)).blob();
      const file = new File([blob], 'selfie.jpg', { type: 'image/jpeg' });

      // Upload to Capture service
      const result = await uploadSelfie(file);

      // Submit to Orchestrate with liveness metadata
      await submitSelfie(session_id, {
        ...result.metadata,
        liveness_score: liveness.livenessScore,
        blink_score: liveness.blinkScore,
        motion_score: liveness.motionScore,
        confidence: liveness.confidence,
        face_centered: liveness.faceCentered,
        face_size: liveness.faceSize,
        liveness_engine: 'mediapipe_facemesh',
        liveness_version: '1.0.0',
      }, result.provider_result);

      // Navigate to review
      router.push('/review');
    } catch (err) {
      console.error('Upload error:', err);
      setError('Upload failed. Please try again.');
      setLoading(false);
      captureAttempted.current = false;
      setCaptured(null);
    }
  };

  const handleCameraError = (err: Error) => {
    console.error('Camera error:', err);
    setCameraError(err.message);
  };

  const handleRetry = () => {
    setError(null);
    setCameraError(null);
    setCaptured(null);
    captureAttempted.current = false;
    engineRef.current.reset();
  };

  return (
    <MobileLayout>
      <div className="flex flex-col items-center">
        <h2 className="text-2xl font-semibold mb-2 text-center">Verify Your Identity</h2>
        <p className="text-sm text-gray-600 mb-6 text-center px-4">
          Look at the camera and follow the on-screen instructions
        </p>

        {/* Error messages */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm w-full">
            <div className="flex items-center justify-between">
              <span>{error}</span>
              <button
                onClick={handleRetry}
                className="ml-2 text-red-700 underline text-xs font-semibold"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {cameraError && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm w-full">
            <p className="font-semibold mb-1">Camera Access Required</p>
            <p className="text-xs">{cameraError}</p>
            <p className="text-xs mt-2">
              Please allow camera access in your browser settings and refresh the page.
            </p>
          </div>
        )}

        {/* Camera feed with adaptive guidance */}
        {!cameraError && (
          <div className="relative w-full max-w-[340px] aspect-[3/4] mb-6">
            {!captured ? (
              <>
                <CameraFeed
                  onResults={handleCameraResults}
                  onError={handleCameraError}
                  width={480}
                  height={640}
                  mirrored={true}
                />
                <AdaptiveGuidanceRing
                  livenessResult={livenessResult}
                  message={guidanceMessage}
                  showRing={true}
                />
              </>
            ) : (
              <div className="relative w-full h-full">
                <img
                  src={captured}
                  alt="Captured selfie"
                  className="w-full h-full object-cover rounded-lg shadow-lg"
                />
                <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 rounded-lg">
                  <div className="text-center">
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
                        <p className="text-white text-sm font-semibold">Verifying...</p>
                      </>
                    ) : (
                      <>
                        <svg
                          className="w-16 h-16 text-green-400 mx-auto mb-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <p className="text-white text-sm font-semibold">Captured!</p>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Liveness info */}
        {!captured && !cameraError && (
          <div className="w-full bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
            <div className="flex items-start space-x-2">
              <svg
                className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div>
                <p className="font-semibold text-blue-900 mb-1">Liveness Detection Active</p>
                <p className="text-blue-700 text-xs">
                  We'll automatically capture your photo when you're positioned correctly.
                  This helps prevent fraud and ensures security.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Manual retry button */}
        {!captured && !loading && !cameraError && (
          <button
            onClick={handleRetry}
            className="mt-4 text-sm text-gray-600 underline"
          >
            Reset and try again
          </button>
        )}
      </div>
    </MobileLayout>
  );
}
