Story: Add getFullName() to Owner returning firstName + space + lastName

Goal
- Add a small accessor on Owner that returns the owner's full name as "<firstName> <lastName>".

Files to change (exact path)
- src/main/java/org/springframework/samples/petclinic/owner/Owner.java

Exact change (patch)
--- a/src/main/java/org/springframework/samples/petclinic/owner/Owner.java
+++ b/src/main/java/org/springframework/samples/petclinic/owner/Owner.java
@@
     @Override
     public String toString() {
         return new ToStringCreator(this).append("id", this.getId())
             .append("new", this.isNew())
             .append("lastName", this.getLastName())
             .append("firstName", this.getFirstName())
             .append("address", this.address)
             .append("city", this.city)
             .append("telephone", this.telephone)
             .toString();
     }
+
+    /**
+     * Return the owner's full name as "firstName lastName".
+     */
+    public String getFullName() {
+        return String.format("%s %s", getFirstName(), getLastName());
+    }
 
***
Notes / rationale
- Only Owner.java needs modification because Owner extends Person and exposes getFirstName()/getLastName().
- No persistence mapping changes required (this is a derived, read-only accessor).
- Optional: add a unit test under src/test/java/org/springframework/samples/petclinic/owner to assert the new method; not required by this story step.

Implementation checklist (next phase)
- Edit Owner.java and add the method exactly as shown.
- Run unit tests and build to verify no regressions.

