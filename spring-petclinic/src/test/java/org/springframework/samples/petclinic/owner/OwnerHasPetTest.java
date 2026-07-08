package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Unit tests for Owner#hasPet(String)
 */
public class OwnerHasPetTest {

	@Test
	void hasPet_returnsTrueForMatchingName() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		p.setId(1);
		owner.getPets().add(p);

		int sizeBefore = owner.getPets().size();

		assertTrue(owner.hasPet("Fido"));

		// read-only: ensure owner state unchanged
		assertEquals(sizeBefore, owner.getPets().size());
		assertEquals("Fido", owner.getPets().get(0).getName());
	}

	@Test
	void hasPet_returnsFalseForNonMatchingName() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		p.setId(1);
		owner.getPets().add(p);

		int sizeBefore = owner.getPets().size();

		assertFalse(owner.hasPet("Rex"));

		// read-only: ensure owner state unchanged
		assertEquals(sizeBefore, owner.getPets().size());
	}

	@Test
	void hasPet_isCaseInsensitive() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("FIDO");
		p.setId(1);
		owner.getPets().add(p);

		assertTrue(owner.hasPet("fido"));
	}

	@Test
	void hasPet_returnsFalseForNullArgument() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		p.setId(1);
		owner.getPets().add(p);

		int sizeBefore = owner.getPets().size();

		assertFalse(owner.hasPet(null));

		// read-only: ensure owner state unchanged
		assertEquals(sizeBefore, owner.getPets().size());
	}

	@Test
	void hasPet_returnsFalseForEmptyString() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		p.setId(1);
		owner.getPets().add(p);

		assertFalse(owner.hasPet(""));
	}

}
