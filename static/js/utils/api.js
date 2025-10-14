const BASE_URL = "http://localhost:8000/api";

export const apiClient = async (url, method = "GET", data = null) => {
  const config = {
    method: method,
    headers: { "Content-Type": "application/json" },
  };

  if (data) config.body = JSON.stringify(data || "{}");

  try {
    const response = await fetch(`${BASE_URL}${url}`, config);

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.message || "request failed");
    }

    return await response.json();
  } catch (error) {
    console.error(error?.status || error);
    throw error;
  }
};
