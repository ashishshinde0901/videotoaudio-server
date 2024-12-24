const express = require("express");
const bodyParser = require("body-parser");
const fs = require("fs");
const path = require("path");

const app = express();
const PORT = 5175;

// Middleware
app.use(bodyParser.json());

// Log directory
const LOG_DIR = path.join(__dirname, "logs");
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR);
}

// Endpoint to receive logs
app.post("/log", (req, res) => {
  try {
    const logData = req.body;

    // Validate log data
    if (!logData.ip || !logData.start_time || !logData.end_time) {
      return res.status(400).json({ error: "Invalid log data" });
    }

    // Generate log file name based on IP and timestamp
    const timestamp = new Date(logData.start_time).toISOString().replace(/[:.]/g, "-");
    const logFileName = `${logData.ip}_${timestamp}.json`;
    const logFilePath = path.join(LOG_DIR, logFileName);

    // Save log data to a file
    fs.writeFileSync(logFilePath, JSON.stringify(logData, null, 2));
    console.log(`Log saved: ${logFilePath}`);

    res.status(200).json({ message: "Log received and stored successfully" });
  } catch (err) {
    console.error("Error saving log:", err);
    res.status(500).json({ error: "Failed to save log" });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on http://127.0.0.1:${PORT}`);
});