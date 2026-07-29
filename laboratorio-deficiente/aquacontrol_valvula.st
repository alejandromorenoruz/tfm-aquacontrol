(*
  AquaControl S.A. - Control de válvula y bomba de la planta de tratamiento
  Fase 2 del TFM: programa de control cargado en OpenPLC.

  Direccionamiento (mapeo automático a Modbus en OpenPLC):
    %QX0.0 Valvula1     -> Coil Modbus 0  (salida digital)
    %QX0.1 Bomba1       -> Coil Modbus 1  (salida digital)
    %IX0.0 NivelBajo    -> Input status 0 (entrada digital, sensor de nivel)

  Lógica legítima: si el nivel del tanque está bajo, se abre la válvula
  y se activa la bomba para rellenar. Este es precisamente el par
  válvula/bomba que se manipulará sin autorización en la Fase 3
  (T0855 - Unauthorized Command Message) escribiendo directamente
  en el coil 0 vía Modbus, sin pasar por esta lógica.
*)

PROGRAM AquaControl
  VAR
    Valvula1    AT %QX0.0 : BOOL;
    Bomba1      AT %QX0.1 : BOOL;
    NivelBajo   AT %IX0.0 : BOOL;
  END_VAR

  IF NivelBajo THEN
    Valvula1 := TRUE;
    Bomba1   := TRUE;
  ELSE
    Valvula1 := FALSE;
    Bomba1   := FALSE;
  END_IF;

END_PROGRAM

CONFIGURATION Config0
  RESOURCE Res0 ON PLC
    TASK Tarea0(INTERVAL := T#100ms, PRIORITY := 0);
    PROGRAM Inst0 WITH Tarea0 : AquaControl;
  END_RESOURCE
END_CONFIGURATION
