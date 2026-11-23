package org.mitre.synthea.modules;

import java.util.Arrays;
import java.util.Collection;
import java.util.Map;

import org.mitre.synthea.helpers.Attributes;
import org.mitre.synthea.helpers.Attributes.Inventory;
import org.mitre.synthea.world.agents.Person;
import org.mitre.synthea.world.concepts.ClinicianSpecialty;
import org.mitre.synthea.world.concepts.HealthRecord.Code;
import org.mitre.synthea.world.concepts.HealthRecord.Encounter;
import org.mitre.synthea.world.concepts.HealthRecord.EncounterType;
import org.mitre.synthea.world.concepts.HealthRecord.Observation;
import org.mitre.synthea.world.concepts.HealthRecord.Report;

/**
 * Module representing the death of a person, certified using the Medical
 * Certificate of Cause of Death (MCCD) for England and Wales, as revised by the
 * Medical Certificate of Cause of Death Regulations 2024 (in force since
 * 9 September 2024).
 *
 * <p>Synthea records a single cause of death per person, so it is entered on
 * MCCD line I(a). With no lower Part I lines, it is also the underlying cause of
 * death.
 */
public class DeathModule {
  /**
   * SNOMED CT code for the death certification procedure.
   */
  public static final Code DEATH_CERTIFICATION = new Code("SNOMED-CT", "308646001",
      "Death certification");

  /**
   * SNOMED CT code for the cause of death, as recorded on the MCCD. This is the
   * Observation code. The value is the SNOMED CT concept for the condition,
   * e.g. 22298006 |Myocardial infarction (disorder)|.
   */
  public static final Code CAUSE_OF_DEATH_CODE = new Code("SNOMED-CT", "184305005",
      "Cause of death");

  /**
   * SNOMED CT code for the death certificate (record artifact). In England and
   * Wales this is the MCCD: the attending practitioner's certificate or the
   * medical examiner's certificate.
   */
  public static final Code DEATH_CERTIFICATE = new Code("SNOMED-CT", "307930005",
      "Death certificate");
  // NOTE: if new codes are added, be sure to update getAllCodes below

  /**
   * Process the death of a person at a given time.
   * @param person the person who has died.
   * @param time the time of the death exam and certification.
   */
  public static void process(Person person, long time) {
    if (!person.alive(time) && person.attributes.containsKey(Person.CAUSE_OF_DEATH)) {
      // create an encounter, diagnostic report, and observation

      Code causeOfDeath = (Code) person.attributes.get(Person.CAUSE_OF_DEATH);

      person.releaseCurrentEncounter(time, "DeathModule");
      Encounter encounter = EncounterModule.createEncounter(person, time, EncounterType.WELLNESS,
          ClinicianSpecialty.GENERAL_PRACTICE, DEATH_CERTIFICATION, "DeathModule");
      encounter.reason = causeOfDeath;

      // MCCD Part I, line I(a): disease or condition directly leading to death.
      Observation codObs = person.record.observation(time, CAUSE_OF_DEATH_CODE.code, causeOfDeath);
      codObs.codes.add(CAUSE_OF_DEATH_CODE);
      codObs.category = "exam";

      // The MCCD, grouping the cause-of-death observation above.
      Report deathCert = person.record.report(time, DEATH_CERTIFICATE.code, 1);
      deathCert.codes.add(DEATH_CERTIFICATE);

      person.record.encounterEnd(time, EncounterType.WELLNESS);
      // Do NOT release the DeathModule encounter, because no one should
      // be able to have an encounter after this one.
    }
  }

  /**
   * Get all of the Codes this module uses, for inventory purposes.
   *
   * @return Collection of all codes and concepts this module uses
   */
  public static Collection<Code> getAllCodes() {
    return Arrays.asList(DEATH_CERTIFICATION, CAUSE_OF_DEATH_CODE, DEATH_CERTIFICATE);
  }

  /**
   * Populate the given attribute map with the list of attributes that this
   * module reads/writes with example values when appropriate.
   *
   * @param attributes Attribute map to populate.
   */
  public static void inventoryAttributes(Map<String,Inventory> attributes) {
    String m = DeathModule.class.getSimpleName();
    // Read
    Attributes.inventory(attributes, m, Person.CAUSE_OF_DEATH, true, false, null);
  }
}
