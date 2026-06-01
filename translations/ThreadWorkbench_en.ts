<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="en_US">

<!-- ══════════════════════════════════════════════════════════════ -->
<!-- Command names (context = command name)                        -->
<!-- ══════════════════════════════════════════════════════════════ -->
<context>
    <name>ThreadCreate</name>
    <message>
        <source>Create thread</source>
        <translation>Create thread</translation>
    </message>
    <message>
        <source>Create a metric thread on a cylindrical face inside a PartDesign::Body</source>
        <translation>Create a metric thread on a cylindrical face inside a PartDesign::Body</translation>
    </message>
</context>
<context>
    <name>ThreadInchCreate</name>
    <message>
        <source>Create inch thread</source>
        <translation>Create inch thread</translation>
    </message>
    <message>
        <source>Create an inch thread (UNC/UNF) on a cylindrical face inside a PartDesign::Body</source>
        <translation>Create an inch thread (UNC/UNF) on a cylindrical face inside a PartDesign::Body</translation>
    </message>
</context>

<!-- ══════════════════════════════════════════════════════════════ -->
<!-- Everything else — context ThreadWorkbench                     -->
<!-- ══════════════════════════════════════════════════════════════ -->
<context>
    <name>ThreadWorkbench</name>

    <!-- Workbench identity (InitGui.py module-level) -->
    <message>
        <source>Thread</source>
        <translation>Thread</translation>
    </message>
    <message>
        <source>Create metric (ISO 724) and inch (UNC/UNF) threads in PartDesign</source>
        <translation>Create metric (ISO 724) and inch (UNC/UNF) threads in PartDesign</translation>
    </message>

    <!-- UI: parameter group -->
    <message>
        <source>ParamGroup</source>
        <translation>Thread parameters</translation>
    </message>
    <message>
        <source>InchDiaLabel</source>
        <translation>Nominal diameter (inch):</translation>
    </message>
    <message>
        <source>InchTPILabel</source>
        <translation>TPI (threads/inch):</translation>
    </message>
    <message>
        <source>PitchMmLabel</source>
        <translation>Pitch (mm, calculated):</translation>
    </message>
    <message>
        <source>Custom</source>
        <translation>— Custom —</translation>
    </message>
    <message>
        <source>DiameterLabel</source>
        <translation>Diameter:</translation>
    </message>
    <message>
        <source>PitchLabel</source>
        <translation>Pitch (mm):</translation>
    </message>
    <message>
        <source>LengthLabel</source>
        <translation>Thread length (mm):</translation>
    </message>
    <message>
        <source>OffsetLabel</source>
        <translation>Offset from edge (mm):</translation>
    </message>
    <message>
        <source>StartEdgeLabel</source>
        <translation>Start from edge:</translation>
    </message>
    <message>
        <source>NoEdge</source>
        <translation>— select a face first —</translation>
    </message>
    <message>
        <source>ClearanceLabel</source>
        <translation>Clearance (mm):</translation>
    </message>
    <message>
        <source>ClearanceTip</source>
        <translation>Radial overlap of the cutting profile with the stock surface.
Increase to cut deeper when stock is oversized (shaft &gt; D)
or undersized (bore &lt; D). Default: 0.05 mm.</translation>
    </message>

    <!-- UI: direction group -->
    <message>
        <source>DirectionGroup</source>
        <translation>Direction</translation>
    </message>
    <message>
        <source>Reversed</source>
        <translation>Reversed direction</translation>
    </message>
    <message>
        <source>LeftHanded</source>
        <translation>Left-handed thread</translation>
    </message>

    <!-- UI: runout combobox -->
    <message>
        <source>RunoutLabel</source>
        <translation>Runout:</translation>
    </message>
    <message>
        <source>RunoutNone</source>
        <translation>None</translation>
    </message>
    <message>
        <source>RunoutPocket</source>
        <translation>Fill (additive)</translation>
    </message>
    <message>
        <source>RunoutTapered</source>
        <translation>Tapered (smooth fade)</translation>
    </message>
    <message>
        <source>RunoutUndercut</source>
        <translation>Undercut (relief groove)</translation>
    </message>
    <message>
        <source>RunoutUndercutNarrow</source>
        <translation>Undercut narrow (form B)</translation>
    </message>
    <message>
        <source>RunoutTip</source>
        <translation>How the thread groove ends:
- None: abrupt stop (milling, tap/die)
- Pocket: additive fill (external)
- Tapered: smooth fade over half a turn (external, real screw runout)
- Undercut: relief groove 3·P (internal, DIN 76-2 form A)
- Undercut narrow: relief groove 2·P (internal, DIN 76-2 form B)</translation>
    </message>

    <!-- UI: misc -->
    <message>
        <source>PresetLabel</source>
        <translation>Preset:</translation>
    </message>
    <message>
        <source>TypeLabel</source>
        <translation>Type:</translation>
    </message>
    <message>
        <source>External</source>
        <translation>External</translation>
    </message>
    <message>
        <source>Internal</source>
        <translation>Internal</translation>
    </message>
    <message>
        <source>EdgeToEdge</source>
        <translation>Edge-to-edge (entire face)</translation>
    </message>
    <message>
        <source>CreateButton</source>
        <translation>Create Thread</translation>
    </message>
    <message>
        <source>StatusDefault</source>
        <translation>Select a cylindrical face on an object inside a PartDesign::Body</translation>
    </message>

    <!-- UI: live preview -->
    <message>
        <source>LivePreview</source>
        <translation>Live preview</translation>
    </message>

    <!-- Status messages -->
    <message>
        <source>status_two_edges</source>
        <translation>✓ Face: R={radius:.2f} mm, face length ≈{face_len:.1f} mm. Edges: #{idx0} and #{idx1}. Choose start edge.</translation>
    </message>
    <message>
        <source>status_one_edge</source>
        <translation>✓ Face: R={radius:.2f} mm. Found 1 edge #{idx0}. Choose start edge.</translation>
    </message>
    <message>
        <source>status_no_edges</source>
        <translation>✓ Face: R={radius:.2f} mm. No round edges found.</translation>
    </message>
    <message>
        <source>no_edges</source>
        <translation>— no edges —</translation>
    </message>

    <!-- Error messages -->
    <message>
        <source>ErrorTitle</source>
        <translation>Error</translation>
    </message>
    <message>
        <source>err_no_document</source>
        <translation>No active document!</translation>
    </message>
    <message>
        <source>err_no_circular_edges</source>
        <translation>No circular edges found on the selected face!</translation>
    </message>
    <message>
        <source>err_no_start_edge</source>
        <translation>Choose a start edge!</translation>
    </message>
    <message>
        <source>err_edge_not_found</source>
        <translation>Chosen edge not found!</translation>
    </message>
    <message>
        <source>TransactionName</source>
        <translation>Create Thread</translation>
    </message>
    <message>
        <source>done</source>
        <translation>✓ Thread created! You can select another face.</translation>
    </message>

    <!-- Builder errors -->
    <message>
        <source>err_nothing_selected</source>
        <translation>Nothing selected.</translation>
    </message>
    <message>
        <source>err_no_subelement</source>
        <translation>Could not determine selected sub-element.</translation>
    </message>
    <message>
        <source>err_cannot_read_face</source>
        <translation>Cannot read face.</translation>
    </message>
    <message>
        <source>err_not_cylindrical</source>
        <translation>Selected face is not cylindrical.</translation>
    </message>
    <message>
        <source>err_not_in_body</source>
        <translation>Object is not inside a PartDesign::Body.</translation>
    </message>
    <message>
        <source>err_not_enough_edges</source>
        <translation>Not enough edges for auto-length. Specify thread length manually.</translation>
    </message>
    <message>
        <source>err_helix_failed</source>
        <translation>Failed to create helix: {e}</translation>
    </message>
    <message>
        <source>err_unknown_profile</source>
        <translation>Unknown thread profile: {pid}</translation>
    </message>
    <message>
        <source>err_runout_failed</source>
        <translation>Failed to create tapered runout: {e}</translation>
    </message>
    <message>
        <source>err_undercut_failed</source>
        <translation>Failed to create undercut runout: {e}</translation>
    </message>

</context>
</TS>
