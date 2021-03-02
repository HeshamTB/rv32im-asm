main:
	addi a1, zero, 0xff
	addi t1, a1, 25
	xor  t2, t1, a1
	call print
print:
	addi a0, zero, 1
	add  a1, t1, zero
	addi a2, zero, 32
	addi a7, zero, 64
	beq a7, zero, print
	ecall
	
