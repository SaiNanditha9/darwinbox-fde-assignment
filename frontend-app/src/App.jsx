import { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [files, setFiles] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const uploadFiles = async () => {
  if (files.length === 0) {
    setError("Please select at least one CSV or Excel file.");
    return;
  }

  setUploading(true);
  setError("");
  setAnswer(null);

  try {
    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: formData,
    });

    const responseText = await response.text();

    let data;

    try {
      data = JSON.parse(responseText);
    } catch {
      throw new Error(
        `Backend returned an invalid response: ${responseText}`
      );
    }

    if (!response.ok) {
      throw new Error(
        data.detail ||
          data.message ||
          "File upload failed."
      );
    }

    console.log("UPLOAD SUCCESS:", data);

    if (!data.files || !Array.isArray(data.files)) {
      throw new Error(
        "Upload succeeded, but the backend did not return the uploaded files."
      );
    }

    setDatasets(data.files);

    // Clear selected files after successful upload
    setFiles([]);

    setError("");
  } catch (err) {
    console.error("UPLOAD ERROR:", err);
    setError(err.message);
  } finally {
    setUploading(false);
  }
};

  const askQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer(null);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to process the question.");
      }

      const data = await response.json();

      setAnswer(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderChart = (result, operation) => {
    if (!result?.data || result.data.length === 0) {
      return null;
    }

    if (operation === "average_salary_by_department") {
      return (
        <div className="chart-card">
          <h4>Average Salary by Department</h4>

          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={result.data}>
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis
                dataKey="department"
                tick={{ fontSize: 13 }}
              />

              <YAxis
                tickFormatter={(value) =>
                  `₹${Number(value).toLocaleString()}`
                }
              />

              <Tooltip
                formatter={(value) =>
                  `₹${Number(value).toLocaleString()}`
                }
              />

              <Bar
                dataKey="average_salary"
                name="Average Salary"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    }

    if (operation === "attendance_trend") {
      return (
        <div className="chart-card">
          <h4>Attendance Trend</h4>

          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={result.data}>
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis
                dataKey="month"
                tick={{ fontSize: 13 }}
              />

              <YAxis
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
              />

              <Tooltip
                formatter={(value) =>
                  `${Number(value).toFixed(2)}%`
                }
              />

              <Line
                type="monotone"
                dataKey="average_attendance"
                name="Average Attendance"
                strokeWidth={3}
                dot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    }

    return null;
  };

  const renderResult = () => {
    if (!answer) {
      return null;
    }

    if (answer.answer && !answer.result) {
      return (
        <div className="answer-card">
          <h3>Answer</h3>
          <p>{answer.answer}</p>
        </div>
      );
    }

    const result = answer.result;

    if (!result) {
      return (
        <div className="answer-card">
          <pre>{JSON.stringify(answer, null, 2)}</pre>
        </div>
      );
    }

    const operation = answer.intent?.operation;

    return (
      <div className="answer-card">
        <div className="answer-header">
          <div>
            <span className="label">Question</span>
            <h3>{answer.question}</h3>
          </div>

          <span className="intent">
            {operation || "analysis"}
          </span>
        </div>

        <div className="main-answer">
          {result.answer}
        </div>

        {renderChart(result, operation)}

        {result.data && result.data.length > 0 && (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  {Object.keys(result.data[0]).map((column) => (
                    <th key={column}>{formatColumnName(column)}</th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {result.data.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, columnIndex) => (
                      <td key={columnIndex}>
                        {formatValue(value)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {result.employee && (
          <div className="employee-card">
            <div>
              <span>Employee</span>
              <strong>{result.employee.name}</strong>
            </div>

            <div>
              <span>Department</span>
              <strong>{result.employee.department}</strong>
            </div>

            <div>
              <span>Annual Salary</span>
              <strong>
                ₹{result.employee.annual_salary.toLocaleString()}
              </strong>
            </div>
          </div>
        )}
      </div>
    );
  };

  const formatColumnName = (column) => {
    return column
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  };

  const formatValue = (value) => {
    if (typeof value === "number") {
      return value.toLocaleString();
    }

    return value;
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <div className="logo">
            Darwinbox <span>AI Data Q&A</span>
          </div>

          <p>
            Upload your employee datasets and ask questions in
            natural language.
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Analysis Ready
        </div>
      </header>

      <main className="container">
        <section className="upload-card">
          <div className="section-title">
            <div>
              <h2>Upload datasets</h2>

              <p>
                Upload employees, attendance, salaries or other
                supported CSV/Excel files.
              </p>
            </div>
          </div>

          <div className="upload-area">
            <input
              type="file"
              multiple
              accept=".csv,.xlsx,.xls"
              onChange={(event) =>
                setFiles(Array.from(event.target.files))
              }
            />

            <div className="upload-icon">↑</div>

            <h3>Choose your data files</h3>

            <p>
              CSV, XLSX or XLS files are supported
            </p>

            {files.length > 0 && (
              <div className="selected-files">
                {files.map((file) => (
                  <span key={file.name}>
                    {file.name}
                  </span>
                ))}
              </div>
            )}

            <button
              className="primary-button"
              onClick={uploadFiles}
              disabled={uploading}
            >
              {uploading
                ? "Uploading..."
                : "Upload files"}
            </button>
          </div>

          {datasets.length > 0 && (
            <div className="datasets">
              <h3>Uploaded datasets</h3>

              <div className="dataset-grid">
                {datasets.map((dataset) => (
                  <div
                    className="dataset-card"
                    key={dataset.filename}
                  >
                    <strong>{dataset.filename}</strong>

                    <span>
                      {dataset.rows} rows
                    </span>

                    <small>
                      {dataset.columns.join(", ")}
                    </small>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="question-card">
          <div className="section-title">
            <div>
              <h2>Ask your data</h2>

              <p>
                Ask a question about the uploaded datasets.
              </p>
            </div>
          </div>

          <div className="question-box">
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="Example: What is the average salary by department?"
              rows="4"
            />

            <button
              className="primary-button ask-button"
              onClick={askQuestion}
              disabled={loading}
            >
              {loading
                ? "Analyzing..."
                : "Ask AI"}
            </button>
          </div>

          <div className="examples">
            <span>Try:</span>

            <button
              onClick={() =>
                setQuestion(
                  "What is the total annual salary of all employees?"
                )
              }
            >
              Total salary
            </button>

            <button
              onClick={() =>
                setQuestion(
                  "What is the average salary by department?"
                )
              }
            >
              Average by department
            </button>

            <button
              onClick={() =>
                setQuestion(
                  "Show employees with attendance above 90%"
                )
              }
            >
              Attendance above 90%
            </button>

            <button
              onClick={() =>
                setQuestion(
                  "Show attendance trend by month"
                )
              }
            >
              Attendance trend
            </button>
          </div>
        </section>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {renderResult()}
      </main>

      <footer>
        Darwinbox FDE Assignment · AI-powered data analysis
      </footer>
    </div>
  );
}

export default App;