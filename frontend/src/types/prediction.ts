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
    [key: string]: {
      price: number | null;
      is_weekend: boolean;
      is_holiday: boolean;
    };
  };
}