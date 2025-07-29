# Scripts for different types of swarms
{
  pkgs,
  uvBoilerplate,
  pythonProject,
  outputs,
  ...
}: let
  inherit (pkgs) lib;

  # Create apps for all workspaces that have executable outputs
  pythonApps = lib.listToAttrs (
    lib.filter (x: x.value != null) (
      map (ws: {
        name = ws.name;
        value =
          if uvBoilerplate.pythonSet ? ${ws.name}
          then {
            type = "app";
            program = "${outputs.packages.${pkgs.system}.${ws.name}}/bin/${ws.name}";
          }
          else null;
      })
      uvBoilerplate.allWorkspaces
    )
  );
in
  {
  }
  // pythonApps
