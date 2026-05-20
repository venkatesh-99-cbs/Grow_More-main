import { apiGet } from "../services/api-service.js";

export function getEmbeddedOffer() {
  const node = document.getElementById("active-offer-data");
  if (!node) return null;
  try {
    return JSON.parse(node.textContent);
  } catch {
    return null;
  }
}

export async function fetchActiveOffers() {
  return apiGet("/api/offers/active/");
}
