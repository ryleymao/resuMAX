import { Card } from "@/components/Card";
import type { ProfileInfo } from "@/app/profile/lib/profile";
import { Button } from "@/components/Button";
import { routes } from "@/lib/routes";

type Props = {
  info: ProfileInfo;
};

export function ProfileOverview({ info }: Props) {
  return (
    <Card tone="neutral" className="space-y-2" id="overview">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-emerald-300">Profile Overview</p>
          <h2 className="text-xl font-semibold text-white">Basic info</h2>
        </div>
        <Button href={routes.upload} variant="secondary" size="md">
          Re-upload Resume
        </Button>
      </div>
      <div className="space-y-2 text-sm text-white/80">
        <p>Name: {info.name || "Unknown"}</p>
        <p>Email: {info.email || "Unknown"}</p>
      </div>
    </Card>
  );
}
