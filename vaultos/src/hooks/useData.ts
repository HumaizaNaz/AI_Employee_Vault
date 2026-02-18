"use client";
import { useState, useEffect, useCallback } from "react";

export function useData<T>(url: string, refreshInterval = 30000) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch_ = useCallback(async () => {
    try {
      const res = await fetch(url);
      const json = await res.json();
      setData(json);
      setError(null);
    } catch (e) {
      setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => {
    fetch_();
    const interval = setInterval(fetch_, refreshInterval);
    return () => clearInterval(interval);
  }, [fetch_, refreshInterval]);

  return { data, loading, error, refetch: fetch_ };
}
