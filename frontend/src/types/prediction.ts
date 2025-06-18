export interface Prediction {
  id: number;
  symbol: string;
  name: string;
  date_time: string;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  positive_probability: number;
  negative_probability: number;
  neutral_probability: number;
  stock_value: number;
  future_prices: {
    "1_day": number | null;
    "2_day": number | null;
    "3_day": number | null;
    "7_day": number | null;
  };
}