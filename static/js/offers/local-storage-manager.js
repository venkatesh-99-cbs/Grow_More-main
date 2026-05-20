const prefix = "gm_offer_";

export const offerStorage = {
  key(name, offerId) {
    return `${prefix}${name}_${offerId || "none"}`;
  },
  get(name, offerId) {
    return localStorage.getItem(this.key(name, offerId));
  },
  set(name, offerId, value = "1") {
    localStorage.setItem(this.key(name, offerId), value);
  },
  remove(name, offerId) {
    localStorage.removeItem(this.key(name, offerId));
  },
};
