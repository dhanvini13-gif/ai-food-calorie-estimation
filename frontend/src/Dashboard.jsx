
import { useEffect, useRef, useState } from "react";
import "./Dashboard.css";

const API_URL = "http://127.0.0.1:8000";

function Dashboard({ accountId }) {
  // Page navigation
  const [currentPage, setCurrentPage] = useState("dashboard");

  // Food analysis
  const [file, setFile] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Daily nutrition
  const [dailySummary, setDailySummary] = useState(null);
  const [summaryLoading, setSummaryLoading] = useState(true);

  // Camera
  const [showCamera, setShowCamera] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const requestInProgress = useRef(false);
  // -----------------------------------------
  // DAILY NUTRITION SUMMARY
  // -----------------------------------------

  const fetchDailySummary = async () => {
    try {
      setSummaryLoading(true);

      const response = await fetch(
  `${API_URL}/daily-summary?account_id=${accountId}`
);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to load daily summary."
        );
      }

      setDailySummary(data);
    } catch (err) {
      console.error("Daily summary error:", err);
    } finally {
      setSummaryLoading(false);
    }
  };

useEffect(() => {
  if (accountId != null) {
    fetchDailySummary();
  }
}, [accountId]);

  // -----------------------------------------
  // SELECT IMAGE FROM GALLERY
  // -----------------------------------------

  const handleGalleryChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    if (!selectedFile.type.startsWith("image/")) {
      setError("Please select a valid image.");
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setError("");
  };

  // -----------------------------------------
  // OPEN CAMERA
  // -----------------------------------------

  const openCamera = async () => {
    setError("");

    if (!navigator.mediaDevices?.getUserMedia) {
      setError(
        "Camera access is unavailable. Use localhost or HTTPS and check your browser permissions."
      );
      return;
    }

    try {
      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: { ideal: "environment" },
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
          audio: false,
        });

      streamRef.current = stream;
      setShowCamera(true);
    } catch (err) {
      console.error("Camera error:", err);

      setError(
        "Unable to access the camera. Allow camera permission and try again."
      );
    }
  };

  // -----------------------------------------
  // CONNECT CAMERA STREAM TO VIDEO
  // -----------------------------------------

  useEffect(() => {
    if (showCamera && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
    }
  }, [showCamera]);

  // -----------------------------------------
  // CLOSE CAMERA
  // -----------------------------------------

  const closeCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });

      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setShowCamera(false);
  };

  // -----------------------------------------
  // CAPTURE PHOTO
  // -----------------------------------------

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || !video.videoWidth) {
      setError("Camera is not ready. Please try again.");
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    if (!context) {
      setError("Unable to capture the image.");
      return;
    }

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setError("Unable to capture the image.");
          return;
        }

        const capturedFile = new File(
          [blob],
          "camera-food.jpg",
          { type: "image/jpeg" }
        );

        setFile(capturedFile);
        setResult(null);
        setError("");

        closeCamera();
      },
      "image/jpeg",
      0.95
    );
  };

  // -----------------------------------------
  // STOP CAMERA WHEN COMPONENT UNMOUNTS
  // -----------------------------------------

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current
          .getTracks()
          .forEach((track) => track.stop());
      }
    };
  }, []);

  // -----------------------------------------
  // NAVIGATE TO FOOD ANALYSIS
  // -----------------------------------------

  const openAnalysisPage = () => {
    setError("");
    setCurrentPage("analysis");
  };

  // -----------------------------------------
  // RETURN TO DASHBOARD
  // -----------------------------------------

  const backToDashboard = () => {
    closeCamera();
    setError("");
    setCurrentPage("dashboard");
    fetchDailySummary();
  };

  // -----------------------------------------
  // ANALYZE FOOD
  // -----------------------------------------

 const handleAnalyze = async (event) => {
    event.preventDefault();

    if (requestInProgress.current) return;
    requestInProgress.current = true;

    if (!file) {
        setError("Please select an image or scan food using the camera.");
        requestInProgress.current = false;
        return;
    }

    const servingQuantity = Number(quantity);

    if (!Number.isFinite(servingQuantity) || servingQuantity <= 0) {
        setError("Quantity must be greater than 0.");
        requestInProgress.current = false;
        return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();

    formData.append("file", file);
    formData.append("quantity", String(servingQuantity));
    formData.append("account_id", String(accountId));

    try {
      console.log("Sending one food prediction request");
        const response = await fetch(
            `${API_URL}/predict`,
            {
                method: "POST",
                body: formData,
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Food analysis failed."
            );
        }

        setResult(data);

        await fetchDailySummary();

    } catch (err) {
        console.error("Food analysis error:", err);

        setError(
            err.message || "Failed to connect to the backend."
        );
    } finally {
    requestInProgress.current = false;
    setLoading(false);
}
};

  // -----------------------------------------
  // LOGOUT
  // -----------------------------------------

  const handleLogout = () => {
    closeCamera();
    window.location.reload();
  };

  // -----------------------------------------
  // PAGE
  // -----------------------------------------

  return (
    <div className="dashboard">

      {/* HEADER */}

      <header className="dashboard-header">
        <div className="brand">

          <div>
            <h1>Food20</h1>
            <p>AI-Powered Food Calorie Estimation</p>
          </div>
        </div>

        <button
          type="button"
          className="logout-button"
          onClick={handleLogout}
        >
          Logout
        </button>
      </header>

      {/* MAIN CONTENT */}

      <main className="dashboard-main">

        {/* =====================================
            PAGE 1: NUTRITION DASHBOARD
        ====================================== */}

        {currentPage === "dashboard" && (
          <>
            {summaryLoading && !dailySummary && (
              <div className="daily-summary-card">
                <p>Loading today's nutrition...</p>
              </div>
            )}

            {dailySummary && (
              <section className="daily-summary-card">
                <div className="summary-header">
                  <div>
                    <h2>Today's Nutrition</h2>

                    <p>
                      Track your daily calorie and
                      macronutrient intake.
                    </p>
                  </div>
                </div>

                <div className="calorie-section">
                  <div className="calorie-circle">
                    <strong>
                      {Math.round(dailySummary.calories)}
                    </strong>

                    <span>kcal</span>
                  </div>

                  <div className="calorie-info">
                    <h3>
                      {Math.round(dailySummary.calories)}
                      {" / "}
                      {Math.round(dailySummary.target)}
                      {" kcal"}
                    </h3>

                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{
                          width: `${Math.min(
                            Math.max(
                              Number(dailySummary.percentage) || 0,
                              0
                            ),
                            100
                          )}%`,
                        }}
                      />
                    </div>

                    <p>
                      {Math.round(dailySummary.remaining)}
                      {" kcal remaining"}
                    </p>
                  </div>
                </div>

                <div className="macro-grid">
                  <div className="macro-card">
                    <span>💪</span>
                    <p>Protein</p>

                    <strong>
                      {Number(
                        dailySummary.protein || 0
                      ).toFixed(1)}
                      {" g"}
                    </strong>
                  </div>

                  <div className="macro-card">
                    <span>🌾</span>
                    <p>Carbs</p>

                    <strong>
                      {Number(
                        dailySummary.carbs || 0
                      ).toFixed(1)}
                      {" g"}
                    </strong>
                  </div>

                  <div className="macro-card">
                    <span>🥑</span>
                    <p>Fat</p>

                    <strong>
                      {Number(
                        dailySummary.fat || 0
                      ).toFixed(1)}
                      {" g"}
                    </strong>
                  </div>
                </div>
              </section>
            )}

            {!summaryLoading && !dailySummary && (
              <section className="daily-summary-card">
                <h2>Today's Nutrition</h2>

                <p>
                  Your nutrition summary is currently
                  unavailable. You can still analyze food.
                </p>

                <button
                  type="button"
                  className="back-button"
                  onClick={fetchDailySummary}
                >
                  Refresh Nutrition
                </button>
              </section>
            )}

            {/* NAVIGATION TO FOOD ANALYSIS */}

            <section className="analysis-navigation-card">
              <div>
                <h2>Analyze Your Food</h2>

                <p>
                  Upload a food image or use your camera
                  to estimate calories and nutrition.
                </p>
              </div>

              <button
                type="button"
                className="analyze-button"
                onClick={openAnalysisPage}
              >
                Analyze Your Food →
              </button>
            </section>
          </>
        )}

        {/* =====================================
            PAGE 2: FOOD ANALYSIS
        ====================================== */}

        {currentPage === "analysis" && (
          <>
            <button
              type="button"
              className="back-button"
              onClick={backToDashboard}
            >
              ← Back to Dashboard
            </button>

            {/* ANALYSIS FORM */}

            <section className="analysis-card">
              <h2>Analyze Your Food</h2>

              <p className="description">
                Upload a food image or scan food using
                your camera.
              </p>

              <form onSubmit={handleAnalyze}>

                {/* IMAGE SELECTION */}

                <label htmlFor="food-file">
                  Food Image
                </label>

                <div className="image-options">

                  <div className="image-option">
                    <input
                      id="food-file"
                      type="file"
                      accept="image/*"
                      onChange={handleGalleryChange}
                      hidden
                    />

                    <label
                      htmlFor="food-file"
                      className="option-button"
                    >
                      Choose from Gallery
                    </label>
                  </div>

                  <div className="image-option">
                    <button
                      type="button"
                      className="option-button camera-button"
                      onClick={openCamera}
                    >
                      Scan with Camera
                    </button>
                  </div>

                </div>

                {/* IMAGE PREVIEW */}

                {file && (
                  <div className="selected-file">
                    <p>
                      Selected: {file.name}
                    </p>

                    <img
                      src={URL.createObjectURL(file)}
                      alt="Selected food"
                      style={{
                        display: "block",
                        width: "100%",
                        maxWidth: "320px",
                        maxHeight: "240px",
                        objectFit: "contain",
                        marginTop: "12px",
                        borderRadius: "12px",
                      }}
                    />

                    <button
                      type="button"
                      className="back-button"
                      onClick={() => {
                        setFile(null);
                        setResult(null);
                        setError("");
                      }}
                      style={{ marginTop: "12px" }}
                    >
                      Remove Image
                    </button>
                  </div>
                )}

                {/* QUANTITY */}

                <label htmlFor="food-quantity">
                  Quantity / Servings
                </label>

                <input
                  id="food-quantity"
                  className="quantity-input"
                  type="number"
                  min="0.5"
                  step="0.5"
                  value={quantity}
                  onChange={(event) =>
                    setQuantity(event.target.value)
                  }
                />

                {/* ERROR */}

                {error && (
                  <div
                    className="error-message"
                    role="alert"
                  >
                    {error}
                  </div>
                )}

                {/* ANALYZE BUTTON */}

                <button
                  type="submit"
                  className="analyze-button"
                  disabled={loading}
              >
                  {loading ? "Analyzing Food..." : "Analyze Food"}
              </button>

              </form>
            </section>

            {/* ANALYSIS RESULT */}

            {result && (
              <section className="result-card">
                <h2>Food Analysis Result</h2>

                <div className="food-name">
                  {result.food}
                </div>

                <div className="confidence">
                  Confidence: {result.confidence}%
                </div>

                <div className="nutrition-grid">

                  <div className="nutrition-item">
                    <span>⚖️</span>
                    <p>Weight</p>

                    <strong>
                      {result.weight}
                    </strong>
                  </div>

                  <div className="nutrition-item">
                    <span>🔥</span>
                    <p>Calories</p>

                    <strong>
                      {result.calories} kcal
                    </strong>
                  </div>

                  <div className="nutrition-item">
                    <span>💪</span>
                    <p>Protein</p>

                    <strong>
                      {result.protein} g
                    </strong>
                  </div>

                  <div className="nutrition-item">
                    <span>🌾</span>
                    <p>Carbs</p>

                    <strong>
                      {result.carbs} g
                    </strong>
                  </div>

                  <div className="nutrition-item">
                    <span>🥑</span>
                    <p>Fat</p>

                    <strong>
                      {result.fat} g
                    </strong>
                  </div>

                </div>

                <button
                  type="button"
                  className="back-button"
                  onClick={() => {
                    setFile(null);
                    setResult(null);
                    setError("");
                  }}
                >
                  Analyze Another Food
                </button>
              </section>
            )}
          </>
        )}

      </main>

      {/* =====================================
          CAMERA MODAL
      ====================================== */}

      {showCamera && (
        <div className="camera-overlay">
          <div className="camera-modal">

            <div className="camera-header">
              <h2>Scan Your Food</h2>

              <button
                type="button"
                className="camera-close"
                onClick={closeCamera}
              >
                ✕
              </button>
            </div>

            <div className="camera-preview">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
              />
            </div>

            <p className="camera-instruction">
              Place the food clearly inside the camera view.
            </p>

            <div className="camera-actions">
              <button
                type="button"
                className="capture-button"
                onClick={capturePhoto}
              >
                📸 Capture Photo
              </button>

              <button
                type="button"
                className="cancel-camera-button"
                onClick={closeCamera}
              >
                Cancel
              </button>
            </div>

          </div>
        </div>
      )}

      {/* HIDDEN CANVAS */}

      <canvas
        ref={canvasRef}
        style={{ display: "none" }}
      />

    </div>
  );
}

export default Dashboard;