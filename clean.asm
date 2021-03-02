main:
	addi a1, zero, 0xff
	sb t1, -100(t2)
	addi t1, a1, 25
	xor  t2, t1, a1
	lui t1, 500
	jal ra, print
print:
	addi a0, zero, 1
	add  a1, t1, zero
	addi a2, zero, 32
	j print
	addi a7, zero, 64
	beq a7, zero, print
	ecall
	
