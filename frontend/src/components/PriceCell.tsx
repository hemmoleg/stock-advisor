interface PriceCellProps {
  futurePrice: {
    price: number | null;
    is_weekend: boolean;
    is_holiday: boolean;
  };
  currentPrice: number;
}

const PriceCell: React.FC<PriceCellProps> = ({ futurePrice, currentPrice }) => {
  const getColorClass = () => {
    if (!futurePrice.price) return 'text-gray-500 dark:text-gray-400';
    return futurePrice.price > currentPrice ? 'text-green-500' : 'text-red-500';
  };

  const getDisplayText = () => {
    if (futurePrice.is_holiday) {
      return <span title="Holiday - No trading">Holiday</span>;
    }
    if (futurePrice.is_weekend) {
      return <span title="Weekend - No trading">Weekend</span>;
    }
    return futurePrice.price ? `$${futurePrice.price.toFixed(2)}` : 'N/A';
  };

  return (
    <td className={`px-6 py-4 ${getColorClass()}`}>
      {getDisplayText()}
    </td>
  );
};

export default PriceCell;