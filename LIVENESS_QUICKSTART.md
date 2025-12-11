# TuringIdentity™ Liveness System - Quick Start Guide

**Get the adaptive liveness system running in 5 minutes**

---

## 🚀 Quick Start (Windows PowerShell)

### **Step 1: Pull Latest Code**

```powershell
cd C:\Users\mjmil\TuringMachines
git pull origin main
```

### **Step 2: Install Frontend Dependencies**

```powershell
cd turing-capture\ui
npm install
```

This installs:
- `@mediapipe/face_mesh` - Face tracking model
- `@mediapipe/camera_utils` - Camera integration
- `@mediapipe/drawing_utils` - Visualization tools

### **Step 3: Run the UI**

```powershell
# From C:\Users\mjmil\TuringMachines
.\RUN_UI_LOCALLY.ps1
```

**Access at**: http://localhost:3001

### **Step 4: Run Backend Services**

Open **3 new PowerShell windows**:

#### **Window 1: TuringCapture (Port 8101)**
```powershell
cd C:\Users\mjmil\TuringMachines\turing-capture
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8101
```

#### **Window 2: TuringOrchestrate (Port 8102)**
```powershell
cd C:\Users\mjmil\TuringMachines\turing-orchestrate
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8102
```

#### **Window 3: TuringRiskBrain (Port 8103)**
```powershell
cd C:\Users\mjmil\TuringMachines\turing-riskbrain
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8103
```

---

## 🧪 Test the Complete Flow

### **1. Open the UI**

Navigate to: http://localhost:3001

### **2. Start Identity Verification**

Click **"Start ID Capture"** on the landing page.

### **3. Upload ID Documents**

- Upload front of ID
- Upload back of ID
- Click **"Continue"**

### **4. Selfie + Liveness Capture**

This is where the magic happens:

1. **Allow camera access** when prompted
2. **Position your face** in the frame
3. **Follow on-screen guidance**:
   - "Move closer" if face is too small
   - "Center your face" if off-center
   - "Hold still" when liveness is being detected
4. **Auto-capture** happens when liveness score > 0.75
5. **Watch the upload** - selfie + liveness metadata sent to backend

### **5. Risk Assessment**

The system automatically:
1. Validates liveness score (must be >= 0.75)
2. Analyzes image quality
3. Calculates risk score
4. Determines risk band (low/medium/high/critical)
5. Routes to appropriate decision page

### **6. Decision Pages**

You'll be routed to one of:
- **✅ Success** - Low risk, approved
- **⚠️ Step-Up** - Medium risk, additional verification
- **📋 Manual Review** - High risk, human review required
- **❌ Rejected** - Critical risk, auto-rejected

---

## 🔍 What to Look For

### **Frontend (Browser)**

1. **Camera Feed**: Should show mirrored video
2. **Guidance Ring**: Color changes based on liveness confidence
   - Red: Needs attention
   - Orange: Improving
   - Yellow: Almost there
   - Green: Perfect
3. **Progress Bar**: Shows liveness score building
4. **Confidence %**: Top-right corner shows detection confidence
5. **Auto-Capture**: Happens automatically when ready

### **Backend Logs**

#### **TuringCapture (Port 8101)**
```
INFO: Biometric upload for session: sess_abc123
INFO: Liveness analysis: {'passed': True, 'score': 0.85, ...}
INFO: Biometric upload result: verified (liveness: True)
```

#### **TuringOrchestrate (Port 8102)**
```
INFO: Submitting selfie for session: sess_abc123
INFO: Selfie submitted for session: sess_abc123 (liveness: True)
INFO: Running risk assessment for session: sess_abc123
INFO: Risk assessment complete: score=18.5, band=low, decision=approved
```

#### **TuringRiskBrain (Port 8103)**
```
INFO: Assessing risk for session: sess_abc123
INFO: Risk assessment complete: score=18.50, band=low, decision=approved
```

---

## 📊 Check API Responses

### **1. Check TuringCapture Health**

```bash
curl http://localhost:8101/health
```

**Expected**:
```json
{
  "status": "ok",
  "service": "turing-capture",
  "version": "2.0.0",
  "timestamp": "2023-12-11T12:00:00Z"
}
```

### **2. Check TuringOrchestrate Health**

```bash
curl http://localhost:8102/health
```

### **3. Check TuringRiskBrain Health**

```bash
curl http://localhost:8103/health
```

### **4. View API Documentation**

- TuringCapture: http://localhost:8101/docs
- TuringOrchestrate: http://localhost:8102/docs
- TuringRiskBrain: http://localhost:8103/docs

---

## 🐛 Troubleshooting

### **Camera Not Working**

**Problem**: "Camera Access Required" error

**Solution**:
1. Check browser permissions: Settings → Privacy → Camera
2. Use HTTPS in production (required for camera access)
3. Try a different browser (Chrome recommended)

### **MediaPipe Not Loading**

**Problem**: "Initializing camera..." stuck

**Solution**:
1. Check internet connection (MediaPipe loads from CDN)
2. Clear browser cache
3. Check console for errors (F12)

### **Liveness Score Always Low**

**Problem**: Liveness score stays below 0.75

**Solution**:
1. Improve lighting (face should be well-lit)
2. Move closer to camera (face should fill 30-50% of frame)
3. Center your face in the frame
4. Blink naturally (don't stare)
5. Move head slightly (micro-motion required)

### **Backend Services Not Starting**

**Problem**: `uvicorn: command not found`

**Solution**:
```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Then run uvicorn
uvicorn main:app --reload --port 8101
```

### **Port Already in Use**

**Problem**: `Address already in use`

**Solution**:
```powershell
# Find process using port 8101
netstat -ano | findstr :8101

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

---

## 📈 Performance Tips

### **For Low-End Devices**

1. **Reduce FPS**: Edit `CameraFeed.tsx`:
   ```typescript
   width: 320,  // Reduced from 480
   height: 426, // Reduced from 640
   ```

2. **Lower Detection Confidence**:
   ```typescript
   minDetectionConfidence: 0.5,  // Reduced from 0.6
   minTrackingConfidence: 0.5,   // Reduced from 0.6
   ```

### **For High-End Devices**

1. **Increase Resolution**: Edit `CameraFeed.tsx`:
   ```typescript
   width: 640,
   height: 853,
   ```

2. **Higher Confidence**:
   ```typescript
   minDetectionConfidence: 0.7,
   minTrackingConfidence: 0.7,
   ```

---

## 🎯 Testing Scenarios

### **Scenario 1: Perfect Capture (Low Risk)**

1. Good lighting
2. Face centered
3. Natural blinking
4. Slight head movement
5. **Expected**: Auto-capture in 2-5 seconds → Success page

### **Scenario 2: Poor Lighting (Medium Risk)**

1. Dim lighting
2. Face partially visible
3. Low liveness score
4. **Expected**: Manual retry → Step-up authentication

### **Scenario 3: Photo Attack (Critical Risk)**

1. Hold photo of face to camera
2. No blinking
3. No motion
4. **Expected**: Liveness check fails → Rejected

---

## 📝 Key Metrics to Monitor

### **Frontend**

- **Liveness Score**: Should reach 0.75+ for auto-capture
- **Confidence**: Should reach 0.80+ for auto-capture
- **Blink Score**: Should be 0.30+ (natural blinking)
- **Motion Score**: Should be 0.20+ (micro-motion)
- **Face Centered**: Should be `true`
- **Face Size**: Should be 0.15-0.85

### **Backend**

- **Liveness Passed**: Should be `true` for low-risk users
- **Quality Score**: Should be 0.70+ for good images
- **Risk Score**: Should be <30 for low-risk
- **Risk Band**: Should be "low" for most users
- **Decision**: Should be "approved" for low-risk

---

## 🎊 Success Criteria

You'll know the system is working when:

1. ✅ Camera feed shows your face
2. ✅ Guidance ring changes color as you adjust position
3. ✅ Liveness score increases over time
4. ✅ Auto-capture happens automatically
5. ✅ Backend logs show liveness validation
6. ✅ Risk assessment returns low risk
7. ✅ You're routed to success page

---

## 🚀 Next Steps

Once the system is working:

1. **Test with different users** - Verify consistency
2. **Test on mobile devices** - iOS Safari, Android Chrome
3. **Test in different lighting** - Bright, dim, backlit
4. **Test spoofing attacks** - Photos, videos, masks
5. **Performance testing** - Load testing with multiple users
6. **Security audit** - Penetration testing
7. **Deploy to staging** - Test with real users
8. **Production deployment** - Go live!

---

## 📚 Additional Resources

- **Full Documentation**: [LIVENESS_SYSTEM.md](./LIVENESS_SYSTEM.md)
- **Architecture**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **API Reference**: http://localhost:8101/docs
- **Developer Guide**: [DEVELOPER_RUNBOOK.md](./DEVELOPER_RUNBOOK.md)

---

## 🆘 Need Help?

- **GitHub Issues**: https://github.com/TuringDynamics3000/TuringMachines/issues
- **Email**: support@turingmachines.io
- **Documentation**: https://docs.turingmachines.io

---

**TuringIdentity™ Liveness System - Up and running in 5 minutes**

*Built with ❤️ by the TuringMachines team*
