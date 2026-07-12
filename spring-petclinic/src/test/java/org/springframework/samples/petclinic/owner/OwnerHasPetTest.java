package org.springframework.samples.petclinic.owner;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class OwnerHasPetTest {

	@Test
	void hasPet_returnsTrue_whenPetNameMatchesExactly() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		owner.getPets().add(p);

		int sizeBefore = owner.getPets().size();
		assertTrue(owner.hasPet("Fido"));
		assertEquals(sizeBefore, owner.getPets().size(), "hasPet should not modify owner's pets");
	}

	@Test
	void hasPet_returnsFalse_whenNoPetMatches() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		owner.getPets().add(p);

		assertFalse(owner.hasPet("Rex"));
		assertEquals(1, owner.getPets().size(), "owner's pets should remain unchanged");
	}

	@Test
	void hasPet_isCaseInsensitive() {
		Owner owner = new Owner();
		Pet p = new Pet();
		p.setName("Fido");
		owner.getPets().add(p);

		assertTrue(owner.hasPet("fIdO"));
	}

	@Test
	void hasPet_returnsFalse_whenNameIsNull() {
		Owner owner = new Owner();

		assertFalse(owner.hasPet(null));
	}

}
