"use client";

import * as React from "react";
import { DropdownMenuCheckboxItemProps } from "@radix-ui/react-dropdown-menu";
import { User, Users, UserCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export type UserRole = "employee" | "hr" | "manager";

interface RoleSelectorProps {
  selectedRole: UserRole;
  onRoleChange: (role: UserRole) => void;
}

const roles = [
  {
    id: "employee" as UserRole,
    label: "Employee",
    icon: User,
    description: "Regular employee access",
  },
  {
    id: "hr" as UserRole,
    label: "HR",
    icon: Users,
    description: "HR department access",
  },
  {
    id: "manager" as UserRole,
    label: "Manager",
    icon: UserCheck,
    description: "Manager level access",
  },
];

export function RoleSelector({
  selectedRole,
  onRoleChange,
}: RoleSelectorProps) {
  const currentRole = roles.find((role) => role.id === selectedRole);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="gap-2">
          {currentRole && <currentRole.icon className="h-4 w-4" />}
          <span className="hidden sm:inline">
            {currentRole?.label || "Select Role"}
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        <DropdownMenuLabel>Select Your Role</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {roles.map((role) => (
          <DropdownMenuItem
            key={role.id}
            onClick={() => onRoleChange(role.id)}
            className={`flex items-center gap-2 cursor-pointer ${
              selectedRole === role.id ? "bg-accent" : ""
            }`}
          >
            <role.icon className="h-4 w-4" />
            <div className="flex flex-col">
              <span className="font-medium">{role.label}</span>
              <span className="text-xs text-muted-foreground">
                {role.description}
              </span>
            </div>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
