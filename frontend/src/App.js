import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const leaveTypes = [
  { code: "AL", label: "Annual Leave" },
  { code: "SL", label: "Sick Leave" },
  { code: "CL", label: "Casual Leave" },
  { code: "MAT", label: "Maternity Leave" },
  { code: "PAT", label: "Paternity Leave" },
  { code: "BRV", label: "Bereavement Leave" },
  { code: "LWP", label: "Leave Without Pay" },
  { code: "WFH", label: "Work From Home" },
];

function App() {
  const [employeeId, setEmployeeId] = useState("EMP-101");
  const [balances, setBalances] = useState([]);
  const [requests, setRequests] = useState([]);
  const [summary, setSummary] = useState(null);
  const [dummyInfo, setDummyInfo] = useState(null);
  const [message, setMessage] = useState("Ready to process your leave workflow.");
  const [formData, setFormData] = useState({
    leave_type_code: "AL",
    start_date: "2026-08-01",
    end_date: "2026-08-05",
    reason: "Detailed planning",
    medical_certificate_submitted: false,
  });

  const fetchBalances = async () => {
    try {
      const response = await axios.get(`/api/leaves/balances/${employeeId}`);
      setBalances(response.data?.balances ?? []);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to load balances.");
      setBalances([]);
    }
  };

  const fetchRequests = async () => {
    try {
      const response = await axios.get(`/api/leaves/requests/${employeeId}`);
      setRequests(response.data);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to load history.");
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await axios.get(`/api/reports/summary/${employeeId}`);
      setSummary(response.data);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to load summary.");
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const payload = { ...formData };
      await axios.post(`/api/leaves/requests/${employeeId}`, payload);
      setMessage("Leave request submitted—waiting approval.");
      setFormData((prev) => ({ ...prev, reason: "" }));
      await fetchBalances();
      await fetchRequests();
      await fetchSummary();
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to submit leave request.");
    }
  };

  const seedDummy = async () => {
    try {
      const response = await axios.post(`/api/dummy/seed`);
      setDummyInfo(response.data);
      setMessage("Dummy data has been seeded for demo work.");
      await fetchBalances();
      await fetchRequests();
      await fetchSummary();
    } catch (error) {
      setMessage(error.response?.data?.detail || "Unable to seed data.");
    }
  };

  useEffect(() => {
    seedDummy();
  }, []);

  return (
    <div className="app-shell">
      <header>
        <h1>Leave Management Console</h1>
        <p className="tone">Policy-aware, empathetic assistant ready to process your leave.</p>
      </header>

      <section className="identity">
        <label>
          Employee ID
          <input value={employeeId} onChange={(e) => setEmployeeId(e.target.value)} />
        </label>
        <button onClick={() => {
          fetchBalances();
          fetchRequests();
          fetchSummary();
        }}>
          Refresh Data
        </button>
      </section>

      <section className="message" aria-live="polite">
        <strong>Action Summary:</strong> {message}
      </section>

      <section className="grid">
        <article className="card shadow">
          <h2>Current Balances</h2>
          {balances?.length ? (
            <ul>
              {balances.map((line) => (
                <li key={line.leave_type_code}>
                  <span>{line.leave_type_code}</span>
                  <strong>{line.remaining.toFixed(1)}</strong>
                  <small>used {line.used.toFixed(1)} / {line.allocated}</small>
                </li>
              ))}
            </ul>
          ) : (
            <p>No balances yet. Seed dummy data first.</p>
          )}
        </article>

        <article className="card shadow">
          <h2>Policy Notes</h2>
          <ul>
            <li>Planned leaves need 7 days advance notice.</li>
            <li>Sick leave longer than 3 days requires medical proof.</li>
            <li>Only 3 teammates can be on approved leave at once.</li>
            <li>Leave balances reset 1st Jan; AL carries forward up to 30 days.</li>
          </ul>
        </article>
      </section>

      <section className="card shadow">
        <h2>New Leave Request</h2>
        <form onSubmit={handleSubmit} className="request-form">
          <label>
            Leave Type
            <select
              value={formData.leave_type_code}
              onChange={(e) => setFormData((prev) => ({ ...prev, leave_type_code: e.target.value }))}
            >
              {leaveTypes.map((option) => (
                <option key={option.code} value={option.code}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Start Date
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData((prev) => ({ ...prev, start_date: e.target.value }))}
              required
            />
          </label>
          <label>
            End Date
            <input
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData((prev) => ({ ...prev, end_date: e.target.value }))}
              required
            />
          </label>
          <label>
            Reason
            <textarea
              rows={2}
              value={formData.reason}
              onChange={(e) => setFormData((prev) => ({ ...prev, reason: e.target.value }))}
              required
            />
          </label>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={formData.medical_certificate_submitted}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, medical_certificate_submitted: e.target.checked }))
              }
            />
            Medical certificate uploaded (if needed)
          </label>
          <button type="submit">Submit Leave Request</button>
        </form>
      </section>

      <section className="card shadow">
        <h2>Leave History</h2>
        {requests.length ? (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Dates</th>
                <th>Status</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((row) => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row.leave_type_code}</td>
                  <td>
                    {row.start_date} → {row.end_date}
                  </td>
                  <td>{row.status}</td>
                  <td>{row.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No requests yet for this employee.</p>
        )}
      </section>

      {summary && (
        <section className="card shadow summary-card">
          <h2>Summary & Upcoming</h2>
          <div className="summary-grid">
            <div>
              <strong>{summary.total_requests}</strong>
              <span>Total requests</span>
            </div>
            <div>
              <strong>{summary.approved}</strong>
              <span>Approved</span>
            </div>
            <div>
              <strong>{summary.pending}</strong>
              <span>Pending</span>
            </div>
            <div>
              <strong>{summary.rejected}</strong>
              <span>Rejected</span>
            </div>
            <div>
              <strong>{summary.upcoming_leaves}</strong>
              <span>Upcoming approved</span>
            </div>
          </div>
        </section>
      )}

      <footer>
        <button onClick={seedDummy}>Regenerate Dummy Data</button>
        <small>Update policy or escalate cases? Contact HR via the provided channels.</small>
      </footer>
    </div>
  );
}

export default App;
