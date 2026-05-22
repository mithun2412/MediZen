import { AlertCircle } from "lucide-react";

export default function InsightCard({
  insight
}) {

  return (

    <div className="
      bg-yellow-50
      border
      border-yellow-200
      rounded-xl
      p-4
      flex
      gap-3
    ">

      <AlertCircle className="text-yellow-600" />

      <p className="text-sm text-gray-700">
        {insight}
      </p>

    </div>
  );
}