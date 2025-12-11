// TuringIdentity™ Adaptive Guidance Ring
// Dynamic visual feedback based on liveness confidence

import React from 'react';
import { LivenessResult } from '../lib/LivenessEngine';

interface AdaptiveGuidanceRingProps {
  livenessResult: LivenessResult;
  message: string;
  showRing?: boolean;
}

export default function AdaptiveGuidanceRing({
  livenessResult,
  message,
  showRing = true,
}: AdaptiveGuidanceRingProps) {
  const { livenessScore, facePresent, faceCentered, faceSize, confidence } = livenessResult;

  // Don't show guidance if high confidence
  if (confidence > 0.9 && livenessScore > 0.8) {
    return (
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="absolute bottom-8 bg-green-500 text-white px-6 py-3 rounded-full shadow-lg animate-pulse">
          <span className="font-semibold">✓ Perfect! Capturing...</span>
        </div>
      </div>
    );
  }

  // Determine ring color based on status
  let ringColor = '#ff4d4d'; // Red - needs attention
  let ringOpacity = 1;

  if (!facePresent) {
    ringColor = '#ff4d4d';
    ringOpacity = 0.8;
  } else if (faceSize < 0.15) {
    ringColor = '#ff9800'; // Orange - move closer
    ringOpacity = 0.9;
  } else if (faceSize > 0.85) {
    ringColor = '#ff9800'; // Orange - move back
    ringOpacity = 0.9;
  } else if (!faceCentered) {
    ringColor = '#f6c34c'; // Yellow - center face
    ringOpacity = 0.85;
  } else if (livenessScore < 0.5) {
    ringColor = '#f6c34c'; // Yellow - improving
    ringOpacity = 0.8;
  } else if (livenessScore < 0.75) {
    ringColor = '#4caf50'; // Green - almost there
    ringOpacity = 0.7;
  } else {
    ringColor = '#4caf50'; // Green - good
    ringOpacity = 0.6;
  }

  // Calculate ring size based on face size
  const ringSize = faceSize < 0.15 ? '50%' : faceSize > 0.85 ? '90%' : '70%';

  // Determine animation
  const shouldPulse = livenessScore < 0.6;
  const shouldGlow = livenessScore >= 0.6 && livenessScore < 0.8;

  return (
    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
      {/* Guidance Ring */}
      {showRing && (
        <div
          className={`rounded-full border-4 transition-all duration-300 ${
            shouldPulse ? 'animate-pulse' : shouldGlow ? 'animate-ping-slow' : ''
          }`}
          style={{
            width: ringSize,
            height: ringSize,
            borderColor: ringColor,
            opacity: ringOpacity,
            boxShadow: shouldGlow ? `0 0 20px ${ringColor}` : 'none',
          }}
        />
      )}

      {/* Face positioning indicators */}
      {facePresent && !faceCentered && (
        <div className="absolute inset-0 flex items-center justify-center">
          {/* Directional arrows */}
          <div className="absolute top-4 text-white text-2xl animate-bounce">↑</div>
          <div className="absolute bottom-4 text-white text-2xl animate-bounce">↓</div>
          <div className="absolute left-4 text-white text-2xl animate-bounce">←</div>
          <div className="absolute right-4 text-white text-2xl animate-bounce">→</div>
        </div>
      )}

      {/* Message overlay */}
      <div className="absolute bottom-8 left-0 right-0 flex justify-center px-4">
        <div
          className="bg-gray-900 bg-opacity-80 text-white px-6 py-3 rounded-full shadow-lg backdrop-blur-sm"
          style={{
            maxWidth: '90%',
          }}
        >
          <div className="flex items-center space-x-2">
            {/* Status icon */}
            {livenessScore < 0.5 ? (
              <svg
                className="w-5 h-5 text-yellow-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            ) : livenessScore < 0.75 ? (
              <svg
                className="w-5 h-5 text-blue-400 animate-spin"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            ) : (
              <svg
                className="w-5 h-5 text-green-400"
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
            )}

            {/* Message text */}
            <span className="text-sm font-semibold">{message}</span>
          </div>

          {/* Progress bar */}
          <div className="mt-2 w-full bg-gray-700 rounded-full h-1.5 overflow-hidden">
            <div
              className="h-full transition-all duration-300 rounded-full"
              style={{
                width: `${Math.min(100, livenessScore * 100)}%`,
                backgroundColor: ringColor,
              }}
            />
          </div>
        </div>
      </div>

      {/* Confidence indicator */}
      {confidence > 0 && (
        <div className="absolute top-4 right-4 bg-gray-900 bg-opacity-70 text-white px-3 py-1 rounded-full text-xs font-mono">
          {Math.round(confidence * 100)}%
        </div>
      )}
    </div>
  );
}
