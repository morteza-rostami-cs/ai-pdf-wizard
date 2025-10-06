const BASE_API = "http://localhost:8000/api";

// generate request instance
async function request(path, options = {}) {
  console.log("request begins!");
  try {
    const response = await fetch(`${BASE_API}${path}`, {
      ...options,
      // cookies for jwt
      credentials: "include",
      headers: {
        // "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    let data;
    const contentType = response.headers.get("content-type");

    if (contentType?.includes("application/json")) {
      data = await response.json();
    } else if (contentType?.includes("text/")) {
      data = await response.text();
    } else {
      // binary stream -> eg: file download
      data = await response.blob();
    }

    // http errors
    if (!response.ok) {
      console.log("what the hell", data);
      // get backend message
      const message = data?.message || data || "api request failed";
      throw new Error(message);
    }
    console.log(data);
    return data;
  } catch (err) {
    console.log("🚨 Fetch failed", err);
    throw err;
  }
}

export const api = {
  getUsers: () => request("/users"),

  // /users/register
  register: (data) =>
    request("/users/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  // /users/login
  login: (data) =>
    request("/users/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),

  // /users/me
  get_me: () =>
    request("/users/me", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      // body: JSON.stringify(data),
    }),

  logout: () =>
    request("/users/logout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    }),

  profile: () =>
    request("/users/profile", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    }),

  pdfUpload: (data) =>
    request("/pdfs/upload-pdf", {
      method: "POST",
      body: data, // do not stringify formData
      // headers: { "Content-Type": "multipart/form-data" }, // let browser to set this
    }),

  fetchPDFs: (data) => request("/pdfs/my-pdfs", { method: "GET" }),

  downloadPDF: (pdf_id) =>
    request(`/pdfs/download/${pdf_id}`, { method: "GET" }),
};
