`timescale 1ns/1ps
module tb_config;
 reg clk=0,rst_n=0;
 reg [7:0] ui=0,uio=31;
 wire [7:0] outp,iop,oep;
 integer i,j,checks=0;
 tt_um_sine_area_detector_adc3542_ddr #(.HANDOFF_WAIT_CYCLES(8)) dut(ui,outp,uio,iop,oep,1'b1,clk,rst_n);
 always #12.207 clk=~clk;
 initial begin
   repeat(4)@(negedge clk);
   rst_n=1;
   for(i=0;i<32;i=i+1)if(i!=1)begin
     uio=i;
     for(j=0;j<12;j=j+1)begin
       @(negedge clk);ui=ui^8'hff;
       if(oep!==8'he0 || dut.config_latched_valid!==0 || dut.history_pointer!==0)$fatal(1,"Unsupported LEVEL enabled %0d",i);
       checks=checks+1;
     end
   end
   uio=1;
   repeat(12)@(negedge clk);
   if(oep!==8'he1 || !dut.config_latched_valid)$fatal(1,"LEVEL1 failed to enable");
   uio=31;repeat(12)@(negedge clk);
   if(oep!==8'he1 || !dut.config_latched_valid)$fatal(1,"Configuration did not stay latched");
   $display("CONFIG_PASS,unsupported_level_checks=%0d",checks);$finish;
 end
endmodule
