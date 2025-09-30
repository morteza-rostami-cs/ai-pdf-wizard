const BASE_API = "http://localhost:8000";

// generate request instance
async function request(path, options = {}) {
  console.log("request begins!");
  try {
    const response = await fetch(`${BASE_API}${path}`, {
      ...options,
      // cookies for jwt
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    });

    let data;
    try {
      data = await response.json();
    } catch (err) {
      // if backend does not return json -> fallback to text response
      data = await response.text();
      console.log(data);
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
};
