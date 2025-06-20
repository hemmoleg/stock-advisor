interface PriceCellProps {
  futurePrice: number | null;
  currentPrice: number;
}

const PriceCell: React.FC<PriceCellProps> = ({ futurePrice, currentPrice }) => {
  const getColorClass = () => {
    if (!futurePrice) return 'text-gray-500 dark:text-gray-400';
    return futurePrice > currentPrice ? 'text-green-500' : 'text-red-500';
  };

  return (
    <td className={`px-6 py-4 ${getColorClass()}`}>
      {futurePrice ? `$${futurePrice.toFixed(2)}` : 'N/A'}
    </td>
  );
};

export default PriceCell;