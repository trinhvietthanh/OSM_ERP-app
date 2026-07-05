import { TripDetail } from "./trip-detail";

export default async function TripPage({
  params,
}: {
  params: Promise<{ tripId: string }>;
}) {
  const { tripId } = await params;
  return <TripDetail tripId={tripId} />;
}
